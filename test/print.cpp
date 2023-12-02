#include <iostream>
#include <chrono>
#include <thread>

int main(int argc, char* argv[])
{
    while(true)
    {
        std::cout << "ping" << std::endl;
        for (int i = 0; i < argc; i++)
        {
            std::cout << argv[i] << " ";
        }
        std::cout << std::endl;

        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
}
