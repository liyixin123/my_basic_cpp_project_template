#define SPDLOG_ACTIVE_LEVEL SPDLOG_LEVEL_DEBUG
#include "spdlog/fmt/ranges.h"
#include "spdlog/spdlog.h"
#include <string_view>
#include <vector>
void foo(int a) {
  for (size_t i = 0; i < a; i++) {
    std::string_view s{"Hello world!"};
    spdlog::info("{}", s.data());
  }
}
int main(int argc, char *argv[]) {

  foo(10);
  std::vector<int> v;
  v.push_back(1);
  v.push_back(1);
  v.push_back(1);

  SPDLOG_INFO("{}", v);
  return 0;
}
