#include <iostream>
#include <string>

int main() {

    std::string buffer;

    while (true){
        std::getline(std::cin, buffer);

        if (buffer.empty()) break;

        std::cout << buffer << std::endl;
    }
    return 0;
}
