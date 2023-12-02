#include <iostream>
#include <chrono>
#include <thread>

int main()
{
    while(true)
    {
        std::cout << "ping" << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
}