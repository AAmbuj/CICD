#include <exception>
#include <iostream>

#include "calculator/calculator_service.h"

int main() try {
  demo::calculator::CalculatorService calculator;

  const double a = 10.0;
  const double b = 5.0;
  const double c = 2.0;

  std::cout << "Calculator Demo:" << std::endl;
  std::cout << a << " + " << b << " = " << calculator.Add(a, b) << std::endl;
  std::cout << a << " + " << b << " + " << c << " = "
            << calculator.Add(a, b, c) << std::endl;
  std::cout << a << " - " << b << " = " << calculator.Subtract(a, b)
            << std::endl;
  std::cout << a << " * " << b << " = " << calculator.Multiply(a, b)
            << std::endl;
  std::cout << a << " / " << b << " = " << calculator.Divide(a, b)
            << std::endl;

  return 0;
} catch (const std::exception& ex) {
  std::cerr << "Error: " << ex.what() << std::endl;
  return 1;
} catch (...) {
  std::cerr << "Error: unknown exception" << std::endl;
  return 1;
}
