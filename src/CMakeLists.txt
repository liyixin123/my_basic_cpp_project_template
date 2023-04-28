add_executable(app main.cpp)

find_package(spdlog CONFIG REQUIRED)

target_link_libraries(app PRIVATE spdlog::spdlog)

install(TARGETS app)
