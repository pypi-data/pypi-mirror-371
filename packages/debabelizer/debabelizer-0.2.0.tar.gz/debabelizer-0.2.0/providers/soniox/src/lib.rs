use async_trait::async_trait;
pub use debabelizer_core::*;

#[derive(Debug, Clone)]
pub enum ProviderConfig {
    Simple(std::collections::HashMap<String, serde_json::Value>),
}

impl ProviderConfig {
    pub fn get_api_key(&self) -> Option<String> {
        match self {
            Self::Simple(map) => map
                .get("api_key")
                .and_then(|v| v.as_str())
                .map(|s| s.to_string()),
        }
    }
    
    pub fn get_value(&self, key: &str) -> Option<&serde_json::Value> {
        match self {
            Self::Simple(map) => map.get(key),
        }
    }
}
use futures::{SinkExt, StreamExt};
use serde::Deserialize;
use serde_json::json;
use std::sync::Arc;
use tokio::sync::{Mutex, mpsc};
use tokio::task::JoinHandle;
use tokio_tungstenite::{connect_async, tungstenite::{self, Message}, WebSocketStream, MaybeTlsStream};
use uuid::Uuid;

const SONIOX_WS_URL: &str = "wss://stt-rt.soniox.com/transcribe-websocket";

// Message-driven architecture types for WebSocket communication
#[derive(Debug)]
enum WebSocketCommand {
    SendAudio(Vec<u8>),
    Close,
}

#[derive(Debug)]
enum WebSocketMessage {
    Transcript(StreamingResult),
    Error(String),
    Closed,
}

#[derive(Debug)]
pub struct SonioxProvider {
    api_key: String,
    model: String,
    auto_detect_language: bool,
}

impl SonioxProvider {
    pub async fn new(config: &ProviderConfig) -> Result<Self> {
        let api_key = config
            .get_api_key()
            .ok_or_else(|| DebabelizerError::Configuration("Soniox API key not found".to_string()))?;
        
        let model = config
            .get_value("model")
            .and_then(|v| v.as_str())
            .unwrap_or("stt-rt-preview")  // Use the working model name
            .to_string();
        
        let auto_detect_language = config
            .get_value("auto_detect_language")
            .and_then(|v| v.as_bool())
            .unwrap_or(true);
        
        Ok(Self { 
            api_key, 
            model,
            auto_detect_language,
        })
    }
}

#[async_trait]
impl SttProvider for SonioxProvider {
    fn name(&self) -> &str {
        "soniox"
    }
    
    async fn transcribe(&self, audio: AudioData) -> Result<TranscriptionResult> {
        // For batch transcription, we'll use streaming and collect results
        let config = StreamConfig {
            session_id: Uuid::new_v4(),
            format: audio.format.clone(),
            interim_results: false,
            language: if self.auto_detect_language { None } else { Some(self.model.clone()) },
            ..Default::default()
        };
        
        let mut stream = self.transcribe_stream(config).await?;
        
        // Send all audio at once
        stream.send_audio(&audio.data).await?;
        stream.close().await?;
        
        // Collect all results
        let mut full_text = String::new();
        let mut words = Vec::new();
        let mut confidence_sum = 0.0;
        let mut confidence_count = 0;
        let mut detected_language = None;
        
        while let Some(result) = stream.receive_transcript().await? {
            if result.is_final {
                full_text.push_str(&result.text);
                full_text.push(' ');
                
                if let Some(result_words) = result.words {
                    words.extend(result_words);
                }
                
                confidence_sum += result.confidence;
                confidence_count += 1;
                
                // Extract language from metadata if available
                if detected_language.is_none() {
                    if let Some(metadata) = &result.metadata {
                        if let Some(lang) = metadata.get("language").and_then(|v| v.as_str()) {
                            detected_language = Some(lang.to_string());
                        }
                    }
                }
            }
        }
        
        Ok(TranscriptionResult {
            text: full_text.trim().to_string(),
            confidence: if confidence_count > 0 {
                confidence_sum / confidence_count as f32
            } else {
                0.0
            },
            language_detected: detected_language.or_else(|| {
                if !self.auto_detect_language {
                    Some(self.model.clone())
                } else {
                    None
                }
            }),
            duration: None,
            words: if words.is_empty() { None } else { Some(words) },
            metadata: None,
        })
    }
    
    async fn transcribe_stream(&self, config: StreamConfig) -> Result<Box<dyn SttStream>> {
        println!("🎯 RUST: Soniox provider - transcribe_stream called for session {}", config.session_id);
        let stream = SonioxStream::new(
            self.api_key.clone(), 
            self.model.clone(), 
            self.auto_detect_language,
            config
        ).await?;
        Ok(Box::new(stream))
    }
    
    async fn list_models(&self) -> Result<Vec<Model>> {
        Ok(vec![
            Model {
                id: "auto".to_string(),
                name: "Auto-detect Language".to_string(),
                languages: vec!["multi".to_string()],
                capabilities: vec![
                    "streaming".to_string(), 
                    "timestamps".to_string(),
                    "language-detection".to_string()
                ],
            },
            Model {
                id: "en".to_string(),
                name: "English".to_string(),
                languages: vec!["en".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "es".to_string(),
                name: "Spanish".to_string(),
                languages: vec!["es".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "fr".to_string(),
                name: "French".to_string(),
                languages: vec!["fr".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "de".to_string(),
                name: "German".to_string(),
                languages: vec!["de".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "it".to_string(),
                name: "Italian".to_string(),
                languages: vec!["it".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "pt".to_string(),
                name: "Portuguese".to_string(),
                languages: vec!["pt".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "nl".to_string(),
                name: "Dutch".to_string(),
                languages: vec!["nl".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "ru".to_string(),
                name: "Russian".to_string(),
                languages: vec!["ru".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "zh".to_string(),
                name: "Chinese".to_string(),
                languages: vec!["zh".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "ja".to_string(),
                name: "Japanese".to_string(),
                languages: vec!["ja".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "ko".to_string(),
                name: "Korean".to_string(),
                languages: vec!["ko".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
            Model {
                id: "hi".to_string(),
                name: "Hindi".to_string(),
                languages: vec!["hi".to_string()],
                capabilities: vec!["streaming".to_string(), "timestamps".to_string()],
            },
        ])
    }
    
    fn supported_formats(&self) -> Vec<AudioFormat> {
        vec![
            AudioFormat::wav(16000),
            AudioFormat::wav(8000),
            AudioFormat::wav(48000),
        ]
    }
    
    fn supports_streaming(&self) -> bool {
        true
    }
}

struct SonioxStream {
    session_id: Uuid,
    command_tx: mpsc::UnboundedSender<WebSocketCommand>,
    result_rx: Arc<Mutex<mpsc::UnboundedReceiver<WebSocketMessage>>>,
    background_task: JoinHandle<()>,
}

impl SonioxStream {
    async fn new(
        api_key: String, 
        model: String, 
        auto_detect_language: bool,
        config: StreamConfig
    ) -> Result<Self> {
        println!("🚀 RUST: SonioxStream::new called for session {}", config.session_id);
        tracing::info!("Creating Soniox WebSocket connection with message-driven architecture");
        
        println!("🌐 RUST: Attempting WebSocket connection to Soniox...");
        
        // Use simple URL connection - Soniox accepts api_key as query param
        let url = format!("{}", SONIOX_WS_URL);
        let (ws_stream, _) = connect_async(&url)
            .await
            .map_err(|e| {
                println!("❌ RUST: WebSocket connection failed: {}", e);
                DebabelizerError::Provider(ProviderError::Network(e.to_string()))
            })?;
        println!("✅ RUST: WebSocket connection established");
        
        // Create channels for communication with background task
        let (command_tx, command_rx) = mpsc::unbounded_channel::<WebSocketCommand>();
        let (result_tx, result_rx) = mpsc::unbounded_channel::<WebSocketMessage>();
        
        let session_id = config.session_id;
        
        // Send configuration
        let sample_rate = config.format.sample_rate;
        let num_channels = config.format.channels;
        
        // Include api_key and model in the config message  
        let init_message = json!({
            "api_key": api_key,
            "audio_format": "pcm_s16le",
            "sample_rate": sample_rate,
            "num_channels": num_channels,
            "model": model,  // Must be exactly "stt-rt-preview"
            "enable_language_identification": auto_detect_language || config.language.is_none(),
            "include_nonfinal": config.interim_results,
        });
        
        // Log the configuration (mask API key)
        let mut log_message = init_message.clone();
        if let Some(api_key_value) = log_message.get_mut("api_key") {
            *api_key_value = json!("***masked***");
        }
        tracing::info!("Sending Soniox configuration: {}", serde_json::to_string_pretty(&log_message).unwrap_or_default());
        
        // Create the background WebSocket handler task
        println!("🔧 RUST: About to spawn WebSocket background handler task for session {}", session_id);
        tracing::info!("🚀 Creating background WebSocket handler task...");
        
        // Clone session_id for the async block
        let task_session_id = session_id;
        
        let background_task = tokio::spawn(async move {
            println!("🔧 RUST: Background task STARTED! Session {}", task_session_id);
            
            // Call the websocket handler directly
            websocket_handler(
                ws_stream, 
                init_message, 
                task_session_id,
                command_rx,
                result_tx
            ).await;
            
            println!("🔧 RUST: Background task FINISHED! Session {}", task_session_id);
        });
        
        println!("✅ RUST: Background task spawned, checking if it's alive...");
        tracing::info!("✅ Soniox WebSocket background task spawned successfully");
        
        // Quick check if task failed immediately
        if background_task.is_finished() {
            println!("❌ RUST: Background task finished immediately - this is a problem!");
        } else {
            println!("✅ RUST: Background task is running");
        }
        
        // Give the task a moment to start and verify it's actually running
        tokio::task::yield_now().await;
        
        // Wait a bit longer and check if the task started
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        
        if background_task.is_finished() {
            println!("❌ RUST: Background task died after yield! Checking for panic...");
            match background_task.await {
                Ok(()) => println!("❌ RUST: Background task completed normally (unexpected)"),
                Err(e) if e.is_panic() => println!("❌ RUST: Background task panicked: {:?}", e),
                Err(e) => println!("❌ RUST: Background task error: {:?}", e),
            }
            return Err(DebabelizerError::Provider(ProviderError::Network("Background WebSocket task failed to start".to_string())));
        } else {
            println!("✅ RUST: Background task is still alive after yield");
        }
        
        Ok(Self {
            session_id,
            command_tx,
            result_rx: Arc::new(Mutex::new(result_rx)),
            background_task,
        })
    }
    
}

async fn websocket_handler(
        mut ws_stream: WebSocketStream<MaybeTlsStream<tokio::net::TcpStream>>,
        init_message: serde_json::Value,
        session_id: Uuid,
        mut command_rx: mpsc::UnboundedReceiver<WebSocketCommand>,
        result_tx: mpsc::UnboundedSender<WebSocketMessage>
    ) {
        println!("🔧 RUST: Starting Soniox WebSocket background handler for session {}", session_id);
        tracing::info!("🔧 Starting Soniox WebSocket background handler for session {}", session_id);
        
        // Send initial configuration and handle handshake
        println!("📤 RUST: Sending initial configuration to Soniox...");
        tracing::info!("📤 Sending initial configuration to Soniox...");
        if let Err(e) = ws_stream.send(Message::Text(init_message.to_string())).await {
            println!("❌ RUST: Failed to send initial configuration: {}", e);
            tracing::error!("Failed to send initial configuration: {}", e);
            let _ = result_tx.send(WebSocketMessage::Error(format!("Initial config failed: {}", e)));
            return;
        }
        println!("✅ RUST: Configuration sent successfully");
        tracing::info!("✅ Configuration sent successfully");
        
        // Wait for handshake response
        println!("⏳ RUST: Waiting for Soniox handshake response...");
        tracing::info!("⏳ Waiting for Soniox handshake response...");
        match ws_stream.next().await {
            Some(Ok(Message::Text(response))) => {
                println!("📥 RUST: Received Soniox handshake: {}", response);
                tracing::info!("📥 Received Soniox handshake: {}", response);
                if let Ok(json_response) = serde_json::from_str::<serde_json::Value>(&response) {
                    if let Some(error) = json_response.get("error") {
                        println!("❌ RUST: Soniox handshake error: {}", error);
                        tracing::error!("Soniox handshake error: {}", error);
                        let _ = result_tx.send(WebSocketMessage::Error(format!("Handshake error: {}", error)));
                        return;
                    }
                    if let Some(error_msg) = json_response.get("error_message") {
                        println!("❌ RUST: Soniox error: {}", error_msg);
                        tracing::error!("Soniox error: {}", error_msg);
                        let _ = result_tx.send(WebSocketMessage::Error(format!("Error: {}", error_msg)));
                        return;
                    }
                }
                println!("✅ RUST: Soniox handshake successful - entering main loop");
                tracing::info!("✅ Soniox handshake successful - entering main loop");
            }
            Some(Ok(other_msg)) => {
                println!("⚠️ RUST: Unexpected handshake message: {:?}", other_msg);
                tracing::warn!("⚠️ Unexpected handshake message: {:?}", other_msg);
            }
            Some(Err(e)) => {
                println!("❌ RUST: Soniox handshake error: {}", e);
                tracing::error!("❌ Soniox handshake error: {}", e);
                let _ = result_tx.send(WebSocketMessage::Error(format!("Handshake error: {}", e)));
                return;
            }
            None => {
                println!("❌ RUST: Soniox WebSocket closed during handshake");
                tracing::error!("❌ Soniox WebSocket closed during handshake");
                let _ = result_tx.send(WebSocketMessage::Error("WebSocket closed during handshake".to_string()));
                return;
            }
        }
        
        // Debug: Confirm we reach this point
        println!("🔧 RUST: About to enter main WebSocket event loop - task still alive");
        tracing::info!("🔧 About to enter main WebSocket event loop - task still alive");
        
        // Main event loop - handle both commands and incoming messages
        println!("🔄 RUST: Entering main WebSocket event loop");
        tracing::info!("🔄 Entering main WebSocket event loop");
        loop {
            println!("🔄 RUST: Main loop iteration starting - task processing commands/messages");
            tracing::debug!("🔄 Loop iteration - waiting for WebSocket messages or commands");
            tokio::select! {
                // Handle commands from the stream (audio chunks, close, etc.)
                command = command_rx.recv() => {
                    match command {
                        Some(WebSocketCommand::SendAudio(audio_data)) => {
                            println!("📤 RUST: Sending {} bytes of audio to Soniox via WebSocket", audio_data.len());
                            tracing::debug!("Sending {} bytes of audio to Soniox", audio_data.len());
                            if let Err(e) = ws_stream.send(Message::Binary(audio_data)).await {
                                tracing::error!("Failed to send audio: {}", e);
                                let _ = result_tx.send(WebSocketMessage::Error(format!("Audio send failed: {}", e)));
                                break;
                            }
                        }
                        Some(WebSocketCommand::Close) => {
                            tracing::info!("Closing WebSocket connection");
                            if let Err(e) = ws_stream.close(None).await {
                                tracing::warn!("Error closing WebSocket: {}", e);
                            }
                            let _ = result_tx.send(WebSocketMessage::Closed);
                            break;
                        }
                        None => {
                            tracing::warn!("❌ Command channel closed, ending WebSocket handler");
                            break;
                        }
                    }
                }
                
                // Handle incoming WebSocket messages
                ws_msg = ws_stream.next() => {
                    match ws_msg {
                        Some(Ok(Message::Text(text))) => {
                            println!("📥 RUST: Received Soniox WebSocket message: {}", text);
                            tracing::debug!("Received Soniox message: {}", text);
                            
                            match serde_json::from_str::<SonioxResponse>(&text) {
                                Ok(response) => {
                                    // Check for errors
                                    if let Some(error) = response.error {
                                        tracing::error!("Soniox error response: {}", error);
                                        let _ = result_tx.send(WebSocketMessage::Error(format!("Soniox error: {}", error)));
                                        continue;
                                    }
                                    if let Some(error_msg) = response.error_message {
                                        tracing::error!("Soniox error message: {}", error_msg);
                                        let _ = result_tx.send(WebSocketMessage::Error(format!("Error: {}", error_msg)));
                                        continue;
                                    }
                                    
                                    // Process tokens if present
                                    if let Some(tokens) = response.tokens {
                                        let streaming_result = process_tokens(tokens, session_id);
                                        println!("📤 RUST: Sending transcription result to Python: '{}'", streaming_result.text);
                                        if let Err(_) = result_tx.send(WebSocketMessage::Transcript(streaming_result)) {
                                            println!("❌ RUST: Failed to send result through channel - receiver dropped");
                                            tracing::error!("Failed to send result through channel - receiver dropped");
                                            break;
                                        }
                                    } else {
                                        // No tokens - send keep-alive
                                        let keep_alive = StreamingResult {
                                            session_id,
                                            is_final: false,
                                            text: String::new(),
                                            confidence: 1.0,
                                            timestamp: chrono::Utc::now(),
                                            words: None,
                                            metadata: Some(json!({"type": "keep-alive", "reason": "status"})),
                                        };
                                        println!("💓 RUST: Sending keep-alive message to Python iterator");
                                        if let Err(_) = result_tx.send(WebSocketMessage::Transcript(keep_alive)) {
                                            println!("❌ RUST: Failed to send keep-alive - receiver dropped");
                                            tracing::error!("Failed to send keep-alive - receiver dropped");
                                            break;
                                        }
                                    }
                                }
                                Err(e) => {
                                    tracing::error!("Failed to parse Soniox response: {} - raw: {}", e, text);
                                    let _ = result_tx.send(WebSocketMessage::Error(format!("Parse error: {}", e)));
                                }
                            }
                        }
                        Some(Ok(Message::Close(_))) => {
                            tracing::info!("WebSocket closed by server");
                            let _ = result_tx.send(WebSocketMessage::Closed);
                            break;
                        }
                        Some(Ok(msg)) => {
                            // Other message types - log them
                            println!("📦 RUST: Received other WebSocket message type: {:?}", msg);
                            tracing::debug!("Received non-text WebSocket message: {:?}", msg);
                        }
                        Some(Err(e)) => {
                            tracing::error!("WebSocket error: {}", e);
                            let _ = result_tx.send(WebSocketMessage::Error(format!("WebSocket error: {}", e)));
                            break;
                        }
                        None => {
                            tracing::info!("WebSocket stream ended");
                            let _ = result_tx.send(WebSocketMessage::Closed);
                            break;
                        }
                    }
                }
            }
        }
        
        tracing::error!("🏁 Soniox WebSocket background handler ended for session {} - this closes the result channel!", session_id);
    }

fn process_tokens(tokens: Vec<SonioxToken>, session_id: Uuid) -> StreamingResult {
        if tokens.is_empty() {
            // Empty tokens array - confirmation message
            return StreamingResult {
                session_id,
                is_final: false,
                text: String::new(),
                confidence: 1.0,
                timestamp: chrono::Utc::now(),
                words: None,
                metadata: Some(json!({"type": "keep-alive", "reason": "confirmation"})),
            };
        }
        
        // Process actual tokens
        let mut full_text = String::new();
        let mut words = Vec::new();
        let mut confidence_sum = 0.0;
        let mut confidence_count = 0;
        let mut is_final = false;
        
        for token in tokens {
            full_text.push_str(&token.text);
            
            if let Some(conf) = token.confidence {
                confidence_sum += conf;
                confidence_count += 1;
            }
            
            if token.is_final {
                is_final = true;
            }
            
            // Create word timing if we have timing info
            if let (Some(start), Some(duration)) = (token.start_time, token.duration) {
                words.push(WordTiming {
                    word: token.text.clone(),
                    start,
                    end: start + duration,
                    confidence: token.confidence.unwrap_or(1.0),
                });
            }
        }
        
        let avg_confidence = if confidence_count > 0 {
            confidence_sum / confidence_count as f32
        } else {
            1.0
        };
        
        StreamingResult {
            session_id,
            is_final,
            text: full_text,
            confidence: avg_confidence,
            timestamp: chrono::Utc::now(),
            words: if words.is_empty() { None } else { Some(words) },
            metadata: None,
        }
    }

#[async_trait]
impl SttStream for SonioxStream {
    async fn send_audio(&mut self, chunk: &[u8]) -> Result<()> {
        tracing::debug!("Sending audio chunk via channel: {} bytes", chunk.len());
        
        self.command_tx
            .send(WebSocketCommand::SendAudio(chunk.to_vec()))
            .map_err(|e| {
                tracing::error!("Failed to send audio command: {}", e);
                DebabelizerError::Provider(ProviderError::Network(format!("Command channel error: {}", e)))
            })?;
        
        tracing::debug!("Audio command sent successfully");
        Ok(())
    }
    
    async fn receive_transcript(&mut self) -> Result<Option<StreamingResult>> {
        tracing::debug!("Receiving transcript from message channel...");
        
        // Check if background task is still running
        if self.background_task.is_finished() {
            tracing::error!("❌ Background WebSocket task has finished!");
            return Ok(None); // End iterator if background task is dead
        }
        
        let mut rx = self.result_rx.lock().await;
        
        // Use timeout to avoid hanging indefinitely
        match tokio::time::timeout(std::time::Duration::from_secs(10), rx.recv()).await {
            Ok(Some(WebSocketMessage::Transcript(result))) => {
                tracing::debug!("Received transcript: '{}' (final: {})", result.text, result.is_final);
                Ok(Some(result))
            }
            Ok(Some(WebSocketMessage::Error(error))) => {
                tracing::error!("Received error message: {}", error);
                Err(DebabelizerError::Provider(ProviderError::Network(error)))
            }
            Ok(Some(WebSocketMessage::Closed)) => {
                tracing::info!("WebSocket connection closed");
                Ok(None) // End iterator
            }
            Ok(None) => {
                tracing::error!("❌ Result channel closed - background task likely exited");
                Ok(None) // End iterator
            }
            Err(_timeout) => {
                tracing::debug!("Timeout waiting for message, sending keep-alive");
                // Instead of ending on timeout, send keep-alive to keep iterator alive
                Ok(Some(StreamingResult {
                    session_id: self.session_id,
                    is_final: false,
                    text: String::new(),
                    confidence: 1.0,
                    timestamp: chrono::Utc::now(),
                    words: None,
                    metadata: Some(json!({"type": "keep-alive", "reason": "receive_timeout"})),
                }))
            }
        }
    }
    
    async fn close(&mut self) -> Result<()> {
        tracing::info!("Closing Soniox stream and background task");
        
        // Send close command
        if let Err(e) = self.command_tx.send(WebSocketCommand::Close) {
            tracing::warn!("Failed to send close command: {}", e);
        }
        
        // Wait for background task to finish (with timeout)
        match tokio::time::timeout(std::time::Duration::from_secs(5), &mut self.background_task).await {
            Ok(result) => {
                if let Err(e) = result {
                    tracing::warn!("Background task error during close: {}", e);
                }
            }
            Err(_) => {
                tracing::warn!("Background task close timeout, aborting");
                self.background_task.abort();
            }
        }
        
        tracing::info!("✅ Soniox stream closed");
        Ok(())
    }
    
    fn session_id(&self) -> Uuid {
        self.session_id
    }
}

#[derive(Debug, Deserialize)]
struct SonioxResponse {
    tokens: Option<Vec<SonioxToken>>,
    final_audio_proc_ms: Option<i32>,
    total_audio_proc_ms: Option<i32>,
    error: Option<String>,
    error_code: Option<i32>,
    error_message: Option<String>,
}

#[derive(Debug, Deserialize)]
struct SonioxToken {
    text: String,
    #[serde(default)]
    is_final: bool,
    confidence: Option<f32>,
    language: Option<String>,
    start_time: Option<f32>,
    duration: Option<f32>,
}

#[derive(Debug, Deserialize)]
struct SonioxWord {
    text: String,
    start_time: f32,
    duration: f32,
    confidence: Option<f32>,
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_provider_creation() {
        let config = ProviderConfig::Simple({
            let mut map = std::collections::HashMap::new();
            map.insert("api_key".to_string(), json!("test-key"));
            map
        });
        
        let provider = SonioxProvider::new(&config).await;
        assert!(provider.is_ok());
    }
    
    #[tokio::test]
    async fn test_auto_detect_language_config() {
        let config = ProviderConfig::Simple({
            let mut map = std::collections::HashMap::new();
            map.insert("api_key".to_string(), json!("test-key"));
            map.insert("auto_detect_language".to_string(), json!(true));
            map
        });
        
        let provider = SonioxProvider::new(&config).await.unwrap();
        assert!(provider.auto_detect_language);
    }
    
    #[test]
    fn test_supported_formats() {
        let provider = SonioxProvider {
            api_key: "test".to_string(),
            model: "en".to_string(),
            auto_detect_language: false,
        };
        
        let formats = provider.supported_formats();
        assert!(!formats.is_empty());
        assert!(formats.iter().any(|f| f.format == "wav"));
    }
    
    #[tokio::test]
    async fn test_list_models_includes_auto() {
        let provider = SonioxProvider {
            api_key: "test".to_string(),
            model: "en".to_string(),
            auto_detect_language: true,
        };
        
        let models = provider.list_models().await.unwrap();
        assert!(models.iter().any(|m| m.id == "auto"));
        assert!(models.iter().any(|m| m.capabilities.contains(&"language-detection".to_string())));
    }

    #[test]
    fn test_provider_config_api_key_extraction() {
        let config = ProviderConfig::Simple({
            let mut map = std::collections::HashMap::new();
            map.insert("api_key".to_string(), json!("my-secret-key"));
            map.insert("model".to_string(), json!("es"));
            map.insert("auto_detect_language".to_string(), json!(false));
            map
        });
        
        assert_eq!(config.get_api_key(), Some("my-secret-key".to_string()));
        assert_eq!(config.get_value("model").unwrap().as_str(), Some("es"));
        assert_eq!(config.get_value("auto_detect_language").unwrap().as_bool(), Some(false));
    }

    #[test]
    fn test_provider_config_missing_api_key() {
        let config = ProviderConfig::Simple({
            let mut map = std::collections::HashMap::new();
            map.insert("model".to_string(), json!("en"));
            map
        });
        
        assert!(config.get_api_key().is_none());
    }

    #[tokio::test]
    async fn test_provider_creation_fails_without_api_key() {
        let config = ProviderConfig::Simple(std::collections::HashMap::new());
        
        let result = SonioxProvider::new(&config).await;
        assert!(result.is_err());
        
        let error = result.unwrap_err();
        assert!(matches!(error, DebabelizerError::Configuration(_)));
    }

    #[tokio::test]
    async fn test_provider_creation_with_custom_model() {
        let config = ProviderConfig::Simple({
            let mut map = std::collections::HashMap::new();
            map.insert("api_key".to_string(), json!("test-key"));
            map.insert("model".to_string(), json!("fr"));
            map
        });
        
        let provider = SonioxProvider::new(&config).await.unwrap();
        assert_eq!(provider.model, "fr");
    }

    #[test]
    fn test_provider_name() {
        let provider = SonioxProvider {
            api_key: "test".to_string(),
            model: "en".to_string(),
            auto_detect_language: false,
        };
        
        assert_eq!(provider.name(), "soniox");
    }

    #[test]
    fn test_supports_streaming() {
        let provider = SonioxProvider {
            api_key: "test".to_string(),
            model: "en".to_string(),
            auto_detect_language: false,
        };
        
        assert!(provider.supports_streaming());
    }

    #[test]
    fn test_supported_formats_contains_multiple_sample_rates() {
        let provider = SonioxProvider {
            api_key: "test".to_string(),
            model: "en".to_string(),
            auto_detect_language: false,
        };
        
        let formats = provider.supported_formats();
        assert!(formats.len() >= 2);
        
        let sample_rates: Vec<u32> = formats.iter().map(|f| f.sample_rate).collect();
        assert!(sample_rates.contains(&16000));
        assert!(sample_rates.contains(&48000));
    }

    #[tokio::test]
    async fn test_list_models_without_auto_detect() {
        let provider = SonioxProvider {
            api_key: "test".to_string(),
            model: "en".to_string(),
            auto_detect_language: false,
        };
        
        let models = provider.list_models().await.unwrap();
        assert!(models.iter().any(|m| m.id == "en"));
        assert!(models.iter().any(|m| m.id == "es"));
        assert!(models.iter().any(|m| m.id == "fr"));
        assert!(models.iter().any(|m| m.id == "de"));
        assert!(models.iter().any(|m| m.id == "hi"));
    }

    #[test]
    fn test_stream_config_default() {
        let config = StreamConfig::default();
        
        assert!(config.language.is_none());
        assert!(config.model.is_none());
        assert!(config.interim_results); // Default is true
        assert!(config.punctuate); // Default is true
        assert!(!config.profanity_filter); // Default is false
    }

    #[test]
    fn test_stream_config_custom() {
        let config = StreamConfig {
            session_id: uuid::Uuid::new_v4(),
            language: Some("en-US".to_string()),
            model: Some("en".to_string()),
            format: AudioFormat::wav(16000),
            interim_results: true,
            punctuate: true,
            profanity_filter: false,
            diarization: true,
            metadata: None,
            enable_word_time_offsets: false,
            enable_automatic_punctuation: false,
            enable_language_identification: false,
        };
        
        assert_eq!(config.language, Some("en-US".to_string()));
        assert_eq!(config.model, Some("en".to_string()));
        assert!(config.interim_results);
        assert!(config.punctuate);
        assert!(config.diarization);
    }

    #[test]
    fn test_soniox_response_parsing() {
        let json_response = r#"{
            "tokens": [
                {
                    "text": "Hello",
                    "start_time": 0.0,
                    "duration": 0.5,
                    "confidence": 0.98,
                    "is_final": false
                },
                {
                    "text": "world",
                    "start_time": 0.6,
                    "duration": 0.4,
                    "confidence": 0.92,
                    "is_final": true
                }
            ],
            "final_audio_proc_ms": 1000,
            "total_audio_proc_ms": 1000
        }"#;
        
        let response: SonioxResponse = serde_json::from_str(json_response).unwrap();
        let tokens = response.tokens.unwrap();
        
        assert_eq!(tokens.len(), 2);
        assert_eq!(tokens[0].text, "Hello");
        assert_eq!(tokens[0].start_time, Some(0.0));
        assert_eq!(tokens[0].duration, Some(0.5));
        assert_eq!(tokens[0].confidence, Some(0.98));
        assert!(!tokens[0].is_final);
        
        assert_eq!(tokens[1].text, "world");
        assert_eq!(tokens[1].start_time, Some(0.6));
        assert_eq!(tokens[1].duration, Some(0.4));
        assert_eq!(tokens[1].confidence, Some(0.92));
        assert!(tokens[1].is_final);
    }

    #[test]
    fn test_soniox_response_minimal() {
        let json_response = r#"{
            "tokens": [
                {
                    "text": "Test",
                    "is_final": false
                }
            ]
        }"#;
        
        let response: SonioxResponse = serde_json::from_str(json_response).unwrap();
        let tokens = response.tokens.unwrap();
        
        assert_eq!(tokens.len(), 1);
        assert_eq!(tokens[0].text, "Test");
        assert!(!tokens[0].is_final);
        assert!(tokens[0].confidence.is_none());
        assert!(tokens[0].language.is_none());
        assert!(tokens[0].start_time.is_none());
        assert!(tokens[0].duration.is_none());
    }

    #[test]
    fn test_soniox_response_empty() {
        let json_response = r#"{}"#;
        
        let response: SonioxResponse = serde_json::from_str(json_response).unwrap();
        assert!(response.tokens.is_none());
    }

    #[test]
    fn test_websocket_url_construction() {
        let _provider = SonioxProvider {
            api_key: "test-key".to_string(),
            model: "en".to_string(),
            auto_detect_language: false,
        };
        
        // Test URL construction logic
        let base_url = "wss://stt-rt.soniox.com/transcribe-websocket";
        assert_eq!(SONIOX_WS_URL, base_url);
    }

    #[test]
    fn test_word_timing_conversion() {
        let soniox_word = SonioxWord {
            text: "hello".to_string(),
            start_time: 1.0,
            duration: 0.5,
            confidence: Some(0.95),
        };
        
        let word_timing = WordTiming {
            word: soniox_word.text.clone(),
            start: soniox_word.start_time,
            end: soniox_word.start_time + soniox_word.duration,
            confidence: soniox_word.confidence.unwrap_or(1.0),
        };
        
        assert_eq!(word_timing.word, "hello");
        assert_eq!(word_timing.start, 1.0);
        assert_eq!(word_timing.end, 1.5);
        assert_eq!(word_timing.confidence, 0.95);
    }

    #[test]
    fn test_auto_detect_language_provider() {
        let provider = SonioxProvider {
            api_key: "test".to_string(),
            model: "auto".to_string(),
            auto_detect_language: true,
        };
        
        assert_eq!(provider.model, "auto");
        assert!(provider.auto_detect_language);
    }

    #[test]
    fn test_provider_constants() {
        assert_eq!(SONIOX_WS_URL, "wss://stt-rt.soniox.com/transcribe-websocket");
    }

    // Test streaming result creation
    #[test]
    fn test_streaming_result_creation() {
        let session_id = uuid::Uuid::new_v4();
        let words = vec![
            WordTiming {
                word: "hello".to_string(),
                start: 0.0,
                end: 0.5,
                confidence: 0.98,
            },
            WordTiming {
                word: "world".to_string(),
                start: 0.6,
                end: 1.0,
                confidence: 0.92,
            },
        ];
        
        let mut result = StreamingResult::new(session_id, "hello world".to_string(), true, 0.95);
        result.words = Some(words.clone());
        
        assert_eq!(result.session_id, session_id);
        assert!(result.is_final);
        assert_eq!(result.text, "hello world");
        assert_eq!(result.confidence, 0.95);
        assert_eq!(result.words.unwrap().len(), 2);
    }

    #[test]
    fn test_model_info_creation() {
        let model = Model {
            id: "soniox-en".to_string(),
            name: "Soniox English Model".to_string(),
            languages: vec!["en".to_string()],
            capabilities: vec!["transcription".to_string(), "streaming".to_string()],
        };
        
        assert_eq!(model.id, "soniox-en");
        assert_eq!(model.name, "Soniox English Model");
        assert_eq!(model.languages.len(), 1);
        assert_eq!(model.capabilities.len(), 2);
    }
}