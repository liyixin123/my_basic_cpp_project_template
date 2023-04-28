#include "spdlog/spdlog.h"
#include <iostream>
#include <string_view>
int main(int argc, char *argv[]) {

  std::string_view s{"Hello world!"};
  spdlog::info("{}", s.data());

  return 0;
}
