#include <stdio.h>
#include <stdlib.h>

void b(char* foo, char* bar)
{
  abort();
}

void a(int val)
{
  b("hello", "world");
}

int main(int argc, char** argv)
{
  a(42);
  return 0;
}
