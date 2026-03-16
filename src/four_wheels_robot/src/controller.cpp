#include <iostream>
#include <chrono>
#include <termios.h>
#include <queue>
#include <thread>
#include <mutex>
#include <unistd.h>
#include <poll.h>
#include <string>
int main(){
struct pollfd pfd = { STDIN_FILENO, POLLIN, 0 };
bool running = true;
while (running )
{
  // Timeout set to 100ms
  std::queue<std::string> keys_buffer;
  std::mutex buffer_muter;



    std::string c;
    // Read exactly 1 byte directly from the OS file descriptor
    if (read(STDIN_FILENO, &c, 1) > 0)
    {
      std::cout << "the value of the press key is " << c << "\n";

      if (keys_buffer.size() < 10)
      {
        keys_buffer.push(c);
      }
    }

}

}