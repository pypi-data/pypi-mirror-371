// Test with raw PCM audio data
use std::collections::HashMap;
use serde_json::json;
use tokio::time::{timeout, Duration};
use uuid::Uuid;

use debabelizer_soniox::{SonioxProvider, ProviderConfig};
use debabelizer_core::*;

#[tokio::main]
async fn main() -> std::result::Result<(), Box<dyn std::error::Error>> {
    println!("🦀 Rust Soniox Raw PCM Test");
    println!("{}", "=".repeat(50));
    
    // Set up API key
    let api_key = "bdd8a3aa338f862ad26295bbfba29ed4132c8b8b78522ffc819ca187ac1a7d5c";
    
    // Create provider config
    let mut config_map = HashMap::new();
    config_map.insert("api_key".to_string(), json!(api_key));
    // Don't include model - Soniox rejects it
    let provider_config = ProviderConfig::Simple(config_map);
    
    // Create provider
    let provider = SonioxProvider::new(&provider_config).await?;
    
    // Try different audio files
    let audio_files = [
        "/home/peter/debabelizer/test.wav",
        "/home/peter/debabelizer/english_sample.wav",
        "/home/peter/debabelizer/spanish_sample.wav",
    ];
    
    let mut audio_data = None;
    for file in &audio_files {
        if let Ok(data) = std::fs::read(file) {
            println!("📊 Loaded WAV file: {} ({} bytes)", file, data.len());
            audio_data = Some(data);
            break;
        }
    }
    
    let audio_data = audio_data.ok_or("No audio file found")?;
    
    // Parse WAV header to get actual PCM data
    if audio_data.len() < 44 {
        return Err("WAV file too small".into());
    }
    
    // Check WAV header
    let riff = std::str::from_utf8(&audio_data[0..4])?;
    let wave = std::str::from_utf8(&audio_data[8..12])?;
    
    if riff != "RIFF" || wave != "WAVE" {
        return Err("Not a valid WAV file".into());
    }
    
    // Find the data chunk
    let mut pos = 12;
    let mut data_start = 0;
    let mut data_size = 0;
    
    while pos < audio_data.len() - 8 {
        let chunk_id = std::str::from_utf8(&audio_data[pos..pos+4])?;
        let chunk_size = u32::from_le_bytes([
            audio_data[pos+4],
            audio_data[pos+5],
            audio_data[pos+6],
            audio_data[pos+7],
        ]);
        
        if chunk_id == "data" {
            data_start = pos + 8;
            data_size = chunk_size as usize;
            break;
        }
        
        pos += 8 + chunk_size as usize;
    }
    
    if data_start == 0 {
        return Err("No data chunk found in WAV file".into());
    }
    
    let pcm_data = &audio_data[data_start..data_start + data_size.min(audio_data.len() - data_start)];
    println!("📊 Found PCM data: {} bytes at offset {}", pcm_data.len(), data_start);
    
    // Create stream config
    let stream_config = StreamConfig {
        session_id: Uuid::new_v4(),
        format: AudioFormat {
            format: "pcm".to_string(), // Try "pcm" instead of "wav"
            sample_rate: 16000,
            channels: 1,
            bit_depth: Some(16),
        },
        interim_results: true,
        language: Some("en".to_string()), // Explicitly set language
        model: None,
        punctuate: true,
        profanity_filter: false,
        diarization: false,
        metadata: None,
        enable_word_time_offsets: true,
        enable_automatic_punctuation: true,
        enable_language_identification: false, // Don't auto-detect when language is set
    };
    
    let mut stream = provider.transcribe_stream(stream_config).await?;
    println!("✅ Stream created!");
    
    // Send PCM data in reasonable chunks
    let chunk_size = 16000; // 0.5 seconds of audio at 16kHz
    let chunks: Vec<_> = pcm_data.chunks(chunk_size).collect();
    
    println!("\n📤 Sending {} chunks of raw PCM audio...", chunks.len());
    
    // Send chunks with small delays
    for (i, chunk) in chunks.iter().enumerate() {
        println!("  📤 Chunk {}/{}: {} bytes", i + 1, chunks.len(), chunk.len());
        stream.send_audio(chunk).await?;
        tokio::time::sleep(Duration::from_millis(100)).await;
    }
    
    println!("\n✅ All audio sent! Waiting for results...");
    
    // Collect results with timeout
    let mut all_results = Vec::new();
    let mut empty_count = 0;
    
    loop {
        match timeout(Duration::from_secs(3), stream.receive_transcript()).await {
            Ok(Ok(Some(result))) => {
                empty_count = 0;
                let text = result.text.trim();
                
                // Log all results, even empty ones
                println!("  📥 Result: text='{}', final={}, conf={:.3}", 
                    text, result.is_final, result.confidence);
                
                if !text.is_empty() {
                    all_results.push(result);
                }
            }
            Ok(Ok(None)) => {
                println!("  🔚 Stream ended");
                break;
            }
            Ok(Err(e)) => {
                println!("  ❌ Error: {:?}", e);
                break;
            }
            Err(_) => {
                empty_count += 1;
                if empty_count >= 2 {
                    println!("  ⏰ No more results");
                    break;
                }
            }
        }
    }
    
    // Display results
    println!("\n📊 Results Summary:");
    println!("  - Total non-empty results: {}", all_results.len());
    
    if !all_results.is_empty() {
        let final_text: String = all_results
            .iter()
            .filter(|r| r.is_final)
            .map(|r| r.text.trim())
            .collect::<Vec<_>>()
            .join(" ");
        
        let all_text: String = all_results
            .iter()
            .map(|r| r.text.trim())
            .collect::<Vec<_>>()
            .join(" ");
        
        if !final_text.is_empty() {
            println!("\n🎉 SUCCESS! Got final transcription!");
            println!("📝 FINAL TEXT: \"{}\"", final_text);
        } else if !all_text.is_empty() {
            println!("\n⚠️ Got interim results only");
            println!("📝 ALL TEXT: \"{}\"", all_text);
        }
    } else {
        println!("\n❌ FAILURE: No transcription results");
        println!("   Speech → ??? (NO TEXT OUTPUT)");
    }
    
    // Close stream
    let _ = stream.close().await;
    println!("\n✅ Test completed!");
    
    Ok(())
}