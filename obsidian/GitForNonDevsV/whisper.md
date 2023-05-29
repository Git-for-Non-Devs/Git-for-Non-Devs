# whisper.cpp  

[[whisper]]

![whisper.cpp](https://user-images.githubusercontent.com/1991296/235238348-05d0f6a4-da44-4900-a1de-d0707e75b763.jpeg)  
  
[![Actions Status](https://github.com/ggerganov/whisper.cpp/workflows/CI/badge.svg)](https://github.com/ggerganov/whisper.cpp/actions)  
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)  
[![npm](https://img.shields.io/npm/v/whisper.cpp.svg)](https://www.npmjs.com/package/whisper.cpp/)  
  
Beta: [v1.4.2](https://github.com/ggerganov/whisper.cpp/releases/tag/v1.4.2) / Stable: [v1.2.1](https://github.com/ggerganov/whisper.cpp/releases/tag/v1.2.1) / [Roadmap | F.A.Q.](https://github.com/ggerganov/whisper.cpp/discussions/126)  
  
High-performance inference of [OpenAI's Whisper](https://github.com/openai/whisper) automatic speech recognition (ASR) model:  
  
- Plain C/C++ implementation without dependencies  
- Apple silicon first-class citizen - optimized via ARM NEON, Accelerate framework and [Core ML](https://github.com/ggerganov/whisper.cpp#core-ml-support)  
- AVX intrinsics support for x86 architectures  
- VSX intrinsics support for POWER architectures  
- Mixed F16 / F32 precision  
- [4-bit and 5-bit integer quantization support](https://github.com/ggerganov/whisper.cpp#quantization)  
- Low memory usage (Flash Attention)  
- Zero memory allocations at runtime  
- Runs on the CPU  
- [Partial GPU support for NVIDIA via cuBLAS](https://github.com/ggerganov/whisper.cpp#nvidia-gpu-support-via-cublas)  
- [Partial OpenCL GPU support via CLBlast](https://github.com/ggerganov/whisper.cpp#opencl-gpu-support-via-clblast)  
- [C-style API](https://github.com/ggerganov/whisper.cpp/blob/master/whisper.h)  
  
Supported platforms:  
  
- [x] Mac OS (Intel and Arm)  
- [x] [iOS](examples/whisper.objc)  
- [x] [Android](examples/whisper.android)  
- [x] Linux / [FreeBSD](https://github.com/ggerganov/whisper.cpp/issues/56#issuecomment-1350920264)  
- [x] [WebAssembly](examples/whisper.wasm)  
- [x] Windows ([MSVC](https://github.com/ggerganov/whisper.cpp/blob/master/.github/workflows/build.yml#L117-L144) and [MinGW](https://github.com/ggerganov/whisper.cpp/issues/168)]  
- [x] [Raspberry Pi](https://github.com/ggerganov/whisper.cpp/discussions/166)  
  
The entire implementation of the model is contained in 2 source files:  
  
- Tensor operations: [ggml.h](ggml.h) / [ggml.c](ggml.c)  
- Transformer inference: [whisper.h](whisper.h) / [whisper.cpp](whisper.cpp)  
  
Having such a lightweight implementation of the model allows to easily integrate it in different platforms and applications.  
As an example, here is a video of running the model on an iPhone 13 device - fully offline, on-device: [whisper.objc](examples/whisper.objc)  
  
https://user-images.githubusercontent.com/1991296/197385372-962a6dea-bca1-4d50-bf96-1d8c27b98c81.mp4  
  
You can also easily make your own offline voice assistant application: [command](examples/command)  
  
https://user-images.githubusercontent.com/1991296/204038393-2f846eae-c255-4099-a76d-5735c25c49da.mp4  
  
Or you can even run it straight in the browser: [talk.wasm](examples/talk.wasm)  
  
## Implementation details  
  
- The core tensor operations are implemented in C ([ggml.h](ggml.h) / [ggml.c](ggml.c))  
- The transformer model and the high-level C-style API are implemented in C++ ([whisper.h](whisper.h) / [whisper.cpp](whisper.cpp))  
- Sample usage is demonstrated in [main.cpp](examples/main)  
- Sample real-time audio transcription from the microphone is demonstrated in [stream.cpp](examples/stream)  
- Various other examples are available in the [examples](examples) folder  
  
The tensor operators are optimized heavily for Apple silicon CPUs. Depending on the computation size, Arm Neon SIMD  
instrisics or CBLAS Accelerate framework routines are used. The latter are especially effective for bigger sizes since  
the Accelerate framework utilizes the special-purpose AMX coprocessor available in modern Apple products.  
  
## Quick start  
  
First clone the repository.  
  
Then, download one of the Whisper models converted in [ggml format](models). For example:  
  
```bash  
bash ./models/download-ggml-model.sh base.en```  
  
If you wish to convert the Whisper models to ggml format yourself, instructions are in [models/README.md](models/README.md).  
  
Now build the [main](examples/main) example and transcribe an audio file like this:  
  
```bash  
# build the main example  
make  
  
# transcribe an audio file  
./main -f samples/jfk.wav  
```  
  
---  
  
For a quick demo, simply run `make base.en`:  
  
```java  
$ make base.en  
  
cc -I. -O3 -std=c11 -pthread -DGGML_USE_ACCELERATE -c ggml.c -o ggml.o  
c++ -I. -I./examples -O3 -std=c++11 -pthread -c whisper.cpp -o whisper.o  
c++ -I. -I./examples -O3 -std=c++11 -pthread examples/main/main.cpp whisper.o ggml.o -o main -framework Accelerate  
./main -h  
  
usage: ./main [options] file0.wav file1.wav ...  
  
options:  
-h, --help [default] show this help message and exit  
-t N, --threads N [4 ] number of threads to use during computation  
-p N, --processors N [1 ] number of processors to use during computation  
-ot N, --offset-t N [0 ] time offset in milliseconds  
-on N, --offset-n N [0 ] segment index offset  
-d N, --duration N [0 ] duration of audio to process in milliseconds  
-mc N, --max-context N [-1 ] maximum number of text context tokens to store  
-ml N, --max-len N [0 ] maximum segment length in characters  
-bo N, --best-of N [5 ] number of best candidates to keep  
-bs N, --beam-size N [-1 ] beam size for beam search  
-wt N, --word-thold N [0.01 ] word timestamp probability threshold  
-et N, --entropy-thold N [2.40 ] entropy threshold for decoder fail  
-lpt N, --logprob-thold N [-1.00 ] log probability threshold for decoder fail  
-su, --speed-up [false ] speed up audio by x2 (reduced accuracy)  
-tr, --translate [false ] translate from source language to english  
-di, --diarize [false ] stereo audio diarization  
-nf, --no-fallback [false ] do not use temperature fallback while decoding  
-otxt, --output-txt [false ] output result in a text file  
-ovtt, --output-vtt [false ] output result in a vtt file  
-osrt, --output-srt [false ] output result in a srt file  
-owts, --output-words [false ] output script for generating karaoke video  
-ocsv, --output-csv [false ] output result in a CSV file  
-of FNAME, --output-file FNAME [ ] output file path (without file extension)  
-ps, --print-special [false ] print special tokens  
-pc, --print-colors [false ] print colors  
-pp, --print-progress [false ] print progress  
-nt, --no-timestamps [true ] do not print timestamps  
-l LANG, --language LANG [en ] spoken language ('auto' for auto-detect)  
--prompt PROMPT [ ] initial prompt  
-m FNAME, --model FNAME [models/ggml-base.en.bin] model path  
-f FNAME, --file FNAME [ ] input WAV file path  
  
  
bash ./models/download-ggml-model.sh base.en  
Downloading ggml model base.en ...  
ggml-base.en.bin 100%[========================>] 141.11M 6.34MB/s in 24s  
Done! Model 'base.en' saved in 'models/ggml-base.en.bin'  
You can now use it like this:  
  
$ ./main -m models/ggml-base.en.bin -f samples/jfk.wav  
  
  
===============================================  
Running base.en on all samples in ./samples ...  
===============================================  
  
----------------------------------------------  
[+] Running base.en on samples/jfk.wav ... (run 'ffplay samples/jfk.wav' to listen)  
----------------------------------------------  
  
whisper_init_from_file: loading model from 'models/ggml-base.en.bin'  
whisper_model_load: loading model  
whisper_model_load: n_vocab = 51864  
whisper_model_load: n_audio_ctx = 1500  
whisper_model_load: n_audio_state = 512  
whisper_model_load: n_audio_head = 8  
whisper_model_load: n_audio_layer = 6  
whisper_model_load: n_text_ctx = 448  
whisper_model_load: n_text_state = 512  
whisper_model_load: n_text_head = 8  
whisper_model_load: n_text_layer = 6  
whisper_model_load: n_mels = 80  
whisper_model_load: f16 = 1  
whisper_model_load: type = 2  
whisper_model_load: mem required = 215.00 MB (+ 6.00 MB per decoder)  
whisper_model_load: kv self size = 5.25 MB  
whisper_model_load: kv cross size = 17.58 MB  
whisper_model_load: adding 1607 extra tokens  
whisper_model_load: model ctx = 140.60 MB  
whisper_model_load: model size = 140.54 MB  
  
system_info: n_threads = 4 / 10 | AVX = 0 | AVX2 = 0 | AVX512 = 0 | FMA = 0 | NEON = 1 | ARM_FMA = 1 | F16C = 0 | FP16_VA = 1 | WASM_SIMD = 0 | BLAS = 1 | SSE3 = 0 | VSX = 0 |  
  
main: processing 'samples/jfk.wav' (176000 samples, 11.0 sec), 4 threads, 1 processors, lang = en, task = transcribe, timestamps = 1 ...  
  
  
[00:00:00.000 --> 00:00:11.000] And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country.  
  
  
whisper_print_timings: fallbacks = 0 p / 0 h  
whisper_print_timings: load time = 113.81 ms  
whisper_print_timings: mel time = 15.40 ms  
whisper_print_timings: sample time = 11.58 ms / 27 runs ( 0.43 ms per run)  
whisper_print_timings: encode time = 266.60 ms / 1 runs ( 266.60 ms per run)  
whisper_print_timings: decode time = 66.11 ms / 27 runs ( 2.45 ms per run)  
whisper_print_timings: total time = 476.31 ms  
```  
  
The command downloads the `base.en` model converted to custom `ggml` format and runs the inference on all `.wav` samples in the folder `samples`.  
  
For detailed usage instructions, run: `./main -h`  
  
Note that the [main](examples/main) example currently runs only with 16-bit WAV files, so make sure to convert your input before running the tool.  
For example, you can use `ffmpeg` like this:  
  
```java  
ffmpeg -i input.mp3 -ar 16000 -ac 1 -c:a pcm_s16le output.wav  
```  
  
## More audio samples  
  
If you want some extra audio samples to play with, simply run:  
  
```  
make samples  
```  
  
This will download a few more audio files from Wikipedia and convert them to 16-bit WAV format via `ffmpeg`.  
  
You can download and run the other models as follows:  
  
```  
make tiny.en  
make tiny  
make base.en  
make base  
make small.en  
make small  
make medium.en  
make medium  
make large-v1  
make large  
```  
  
## Memory usage  
  
| Model | Disk | Mem | SHA |  
| --- | --- | --- | --- |  
| tiny | 75 MB | ~125 MB | `bd577a113a864445d4c299885e0cb97d4ba92b5f` |  
| base | 142 MB | ~210 MB | `465707469ff3a37a2b9b8d8f89f2f99de7299dac` |  
| small | 466 MB | ~600 MB | `55356645c2b361a969dfd0ef2c5a50d530afd8d5` |  
| medium | 1.5 GB | ~1.7 GB | `fd9727b6e1217c2f614f9b698455c4ffd82463b4` |  
| large | 2.9 GB | ~3.3 GB | `0f4c8e34f21cf1a914c59d8b3ce882345ad349d6` |  
  
## Quantization  
  
`whisper.cpp` supports integer quantization of the Whisper `ggml` models.  
Quantized models require less memory and disk space and depending on the hardware can be processed more efficiently.  
  
Here are the steps for creating and using a quantized model:  
  
```bash  
# quantize a model with Q5_0 method  
make quantize  
./quantize models/ggml-base.en.bin models/ggml-base.en-q5_0.bin q5_0  
  
# run the examples as usual, specifying the quantized model file  
./main -m models/ggml-base.en-q5_0.bin ./samples/gb0.wav  
```  
  
## Core ML support  
  
On Apple Silicon devices, the Encoder inference can be executed on the Apple Neural Engine (ANE) via Core ML. This can result in significant  
speed-up - more than x3 faster compared with CPU-only execution. Here are the instructions for generating a Core ML model and using it with `whisper.cpp`:  
  
- Install Python dependencies needed for the creation of the Core ML model:  
  
```bash  
pip install ane_transformerspip install openai-whisperpip install coremltools```  
  
- To ensure `coremltools` operates correctly, please confirm that [Xcode](https://developer.apple.com/xcode/) is installed and execute `xcode-select --install` to install the command-line tools.  
- Python 3.10 is recommended.  
- [OPTIONAL] It is recommended to utilize a Python version management system, such as [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for this step:  
- To create an environment, use: `conda create -n py310-whisper python=3.10 -y`  
- To activate the environment, use: `conda activate py310-whisper`  
  
- Generate a Core ML model. For example, to generate a `base.en` model, use:  
  
```bash  
./models/generate-coreml-model.sh base.en```  
  
This will generate the folder `models/ggml-base.en-encoder.mlmodelc`  
  
- Build `whisper.cpp` with Core ML support:  
  
```bash  
# using Makefile  
make clean  
WHISPER_COREML=1 make -j  
  
# using CMake  
cd build  
cmake -DWHISPER_COREML=1 ..  
```  
  
- Run the examples as usual. For example:  
  
```bash  
./main -m models/ggml-base.en.bin -f samples/jfk.wav  
...  
  
whisper_init_state: loading Core ML model from 'models/ggml-base.en-encoder.mlmodelc'whisper_init_state: first run on a device may take a while ...whisper_init_state: Core ML model loaded  
system_info: n_threads = 4 / 10 | AVX = 0 | AVX2 = 0 | AVX512 = 0 | FMA = 0 | NEON = 1 | ARM_FMA = 1 | F16C = 0 | FP16_VA = 1 | WASM_SIMD = 0 | BLAS = 1 | SSE3 = 0 | VSX = 0 | COREML = 1 |  
...  
```  
  
The first run on a device is slow, since the ANE service compiles the Core ML model to some device-specific format.  
Next runs are faster.  
  
For more information about the Core ML implementation please refer to PR [#566](https://github.com/ggerganov/whisper.cpp/pull/566).  
  
## NVIDIA GPU support via cuBLAS  
  
With NVIDIA cards, the Encoder processing can be offloaded to the GPU to a large extend through cuBLAS.  
First, make sure you have installed `cuda`: https://developer.nvidia.com/cuda-downloads  
  
Now build `whisper.cpp` with cuBLAS support:  
  
```  
make clean  
WHISPER_CUBLAS=1 make -j  
```  
  
## OpenCL GPU support via CLBlast  
  
For cards and integrated GPUs that support OpenCL, the Encoder processing can be largely offloaded to the GPU through CLBlast. This is especially useful for users with AMD APU's or low end devices for up to ~2x speedup.  
  
First, make sure you have installed `CLBlast` for your OS or Distribution: https://github.com/CNugteren/CLBlast  
  
Now build `whisper.cpp` with CLBlast support:  
  
```  
Makefile:  
cd whisper.cpp  
make clean  
WHISPER_CLBLAST=1 make -j  
  
CMake:  
cd whisper.cpp ; mkdir build ; cd build  
cmake -DWHISPER_CLBLAST=ON ..  
make clean  
make -j  
cp bin/* ../  
```  
  
  
Run all the examples as usual.  
  
## Limitations  
  