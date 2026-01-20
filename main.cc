#include <iostream>
#include "calculator.h"

int main() {
  demo::Calculator calc;
  
  // Simple demonstration
  double a = 10.0;
  double b = 5.0;

  std::cout << "Calculator Demo:" << std::endl;
  std::cout << a << " + " << b << " = " << calc.Add(a, b) << std::endl;
  std::cout << a << " - " << b << " = " << calc.Subtract(a, b) << std::endl;
  std::cout << a << " * " << b << " = " << calc.Multiply(a, b) << std::endl;
  std::cout << a << " / " << b << " = " << calc.Divide(a, b) << std::endl;

  return 0;
}