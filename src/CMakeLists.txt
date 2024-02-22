add_executable(app main.cpp)

find_package(spdlog CONFIG REQUIRED)
find_package(Catch2 CONFIG REQUIRED)

target_link_libraries(app PRIVATE spdlog::spdlog)

add_executable(test test.cpp)
target_link_libraries(test PRIVATE Catch2::Catch2WithMain)

install(TARGETS app)
