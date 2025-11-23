"""常见系统头文件行数估算映射"""

# 这些估算值基于典型的C++标准库实现，实际行数可能因实现而异。
# 所有映射均以头文件名为键，估算的行数为值。


SYSTEM_HEADER = {
    "<iostream>": 2500,
    "<vector>": 1800,
    "<string>": 1200,
    "<map>": 2200,
    "<algorithm>": 2000,
    "<memory>": 1500,
    "<list>": 1600,
    "<set>": 1700,
    "<unordered_map>": 2300,
    "<unordered_set>": 2100,
    "<array>": 800,
    "<queue>": 1200,
    "<stack>": 1000,
    "<fstream>": 1500,
    "<sstream>": 1300,
    "<cstdio>": 800,
    "<cstdlib>": 700,
    "<cmath>": 1800,
    "<thread>": 2000,
    "<mutex>": 1200,
    "<atomic>": 1500,
    "<chrono>": 1600,
    "<functional>": 1800,
    "<tuple>": 1400,
    "<type_traits>": 2200,
    "<utility>": 900,
    "<limits>": 600,
    "<stdexcept>": 800,
    "<exception>": 700,
    "<cassert>": 300,
    "<cstring>": 600,
    "<cctype>": 400,
    "<cstddef>": 500,
    "<cstdint>": 600,
    "<cstdarg>": 400,
    "<csetjmp>": 300,
    "<csignal>": 400,
    "<cfloat>": 500,
    "<climits>": 500,
    "<cstdalign>": 200,
    "<cstdbool>": 200,
    "<ctime>": 600,
    "<cuchar>": 300,
    "<cwchar>": 800,
    "<cwctype>": 500,
    "<bitset>": 1000,
    "<complex>": 1500,
    "<deque>": 1400,
    "<forward_list>": 1200,
    "<iterator>": 1600,
    "<numeric>": 1000,
    "<random>": 2500,
    "<ratio>": 1200,
    "<regex>": 2800,
    "<scoped_allocator>": 1500,
    "<system_error>": 800,
    "<typeindex>": 700,
    "<typeinfo>": 600,
    "<valarray>": 2000,
    "<boost/>": 3000,
    "<qt>": 4000,
    "<eigen3/>": 5000,
    "<opencv2/>": 6000,
}

# 外部库模式匹配和默认行数
EXTERNAL_LIB = {
    "boost/": 3000,  # Boost库通常较大
    "eigen3/": 5000,  # Eigen数学库
    "opencv2/": 6000,  # OpenCV计算机视觉库
    "qt": 4000,  # Qt框架
    "gtest/": 1500,  # Google Test
    "gmock/": 1800,  # Google Mock
    "spdlog/": 1200,  # spdlog日志库
    "fmt/": 1500,  # {fmt}格式化库
    "cereal/": 2000,  # cereal序列化库
    "nlohmann/": 2500,  # JSON库
    "catch2/": 1800,  # Catch2测试框架
    "asio/": 3500,  # Asio网络库
    "absl/": 2800,  # Abseil库
    "protobuf/": 4000,  # Protocol Buffers
    "grpc/": 4500,  # gRPC库
    "mongocxx/": 3500,  # MongoDB C++驱动
    "sqlite3.h": 8000,  # SQLite3
    "mysql.h": 7000,  # MySQL客户端
    "pqxx/": 3000,  # PostgreSQL C++接口
    "curl/": 2500,  # libcurl
    "openssl/": 8000,  # OpenSSL
    "zlib.h": 5000,  # zlib压缩库
    "png.h": 6000,  # libpng
    "jpeglib.h": 5500,  # libjpeg
    "freetype2/": 7000,  # FreeType
    "sdl2/": 4000,  # SDL2
    "glfw/": 3500,  # GLFW
    "opengl/": 3000,  # OpenGL
    "vulkan/": 8000,  # Vulkan
    "cuda/": 10000,  # CUDA
    "cudnn.h": 12000,  # cuDNN
    "tensorflow/": 15000,  # TensorFlow
    "torch/": 12000,  # PyTorch
}
