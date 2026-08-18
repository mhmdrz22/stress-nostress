# 🧠 ArameshYar (آرامشیار) - Neuro-Symbolic Edge AI 

[![Kotlin](https://img.shields.io/badge/Kotlin-2.1.0-blue.svg?logo=kotlin)](https://kotlinlang.org)
[![Jetpack Compose](https://img.shields.io/badge/Jetpack%20Compose-Modern%20UI-4285F4?logo=android)](https://developer.android.com/jetpack/compose)
[![TensorFlow Lite](https://img.shields.io/badge/TensorFlow%20Lite-Edge%20AI-FF6F00?logo=tensorflow)](https://www.tensorflow.org/lite)
[![Architecture](https://img.shields.io/badge/Architecture-MVI%20%7C%20Neuro--Symbolic-success)](#system-architecture)

**ArameshYar** is an offline-first, privacy-preserving Android application designed to detect and manage psychological stress. By leveraging a **Neuro-Symbolic AI architecture** directly on the edge (mobile device), it provides highly accurate stress detection, personalized psychological interventions, and coping mechanisms without requiring an internet connection.

---

## ✨ Core Features

*   **Offline-First & Zero-Dependency:** fully functional without internet access, bypassing network restrictions and ensuring 100% availability.
*   **Edge AI Inference:** Uses a quantized (Int8) Deep Learning model via **TensorFlow Lite** for blazing-fast, on-device NLP processing (< 20ms latency).
*   **Local RAG (Retrieval-Augmented Generation):** Implements a Jaccard Similarity algorithm over a local JSON dataset to extract context-aware empathy messages and targeted video search queries.
*   **Privacy by Design:** User inputs and psychological states never leave the device. All historical data is encrypted using **SQLCipher** and hardware-backed Android Keystore.
*   **Interactive Coping Tools:** Includes a built-in Native Text-to-Speech (TTS) engine, a synchronized 4-7-8 visual breathing exercise, and an offline ambient audio player.

---

## 🏛️ System Architecture

The application implements a robust **MVI (Model-View-Intent)** presentation pattern combined with a **Neuro-Symbolic AI** core, heavily inspired by modern intelligent agents:

1.  **Perception Layer (Neural Network):** A lightweight Keras Sequential model (compiled to `.tflite`) acts as the "sensor." It tokenizes Persian text inputs and performs binary/multi-class classification to detect stress levels efficiently without out-of-memory (OOM) risks.
2.  **Reasoning Layer (Knowledge Graph & RAG):** The neural network's output is fed into an algorithmic "Critic" (`LocalAdviceGraph` and `LocalJsonRagEngine`). This layer prevents AI hallucinations by mapping the detected stress type (e.g., Burnout, Anger, Sleep Deprivation) to psychologically safe, pre-verified therapeutic responses.
3.  **Graceful Degradation:** A circuit-breaker pattern ensures that if external APIs (like Gemini) fail or network times out, the app seamlessly falls back to the local RAG engine, completely hiding the failure from the user.

---

## 🛠️ Tech Stack

**Android Development:**
*   **UI:** Jetpack Compose (featuring Glassmorphism design)
*   **Architecture:** MVI (StateFlow, Coroutines), Clean Architecture
*   **Dependency Injection:** Dagger-Hilt
*   **Local Storage:** Room Database + SQLCipher (AES-256 Encryption)

**Machine Learning & MLOps:**
*   **Frameworks:** TensorFlow, Keras, TFLite Support
*   **Optimization:** Model Quantization (Float32 to Int8)
*   **MLOps Dashboard:** Included `admin_dashboard.py` (built with Streamlit) for local data augmentation, anti-overfit training (Early Stopping), and real-time metric visualization.

---

## 🚀 Getting Started

### 1. Run the MLOps Dashboard (Model Training)
To train the model and generate the `.tflite` file:
```bash
pip install streamlit pandas matplotlib tensorflow
streamlit run admin_dashboard.py
```
Upload your train.csv and test.csv datasets to generate stress_model_quantized.tflite and vocab.json.

### 2. Android Build Setup
Move the generated stress_model_quantized.tflite and vocab.json into the app/src/main/assets/ directory.

Ensure `androidResources { noCompress += "tflite" }` is present in your build.gradle.kts to prevent memory-mapping crashes.

Build and run the project via Android Studio.

## 🛡️ Security & Performance
**Anti-Compression**: TFLite models are kept uncompressed in the APK to allow direct memory mapping (MMap), saving valuable RAM.

**State Management**: Native TextToSpeech instances are tied to Compose lifecycles (DisposableEffect) to strictly prevent memory leaks.
