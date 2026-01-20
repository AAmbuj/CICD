#include "calculator.h"
#include <stdexcept>

namespace demo {

double Calculator::Add(double a, double b) {
  return a + b;
}

double Calculator::Add(double a, double b, double c) {
  return a + b + c;
}

double Calculator::Subtract(double a, double b) {
  return a - b;
}

double Calculator::Multiply(double a, double b) {
  return a * b;
}

double Calculator::Divide(double a, double b) {
  if (b == 0) {
    throw std::invalid_argument("Cannot divide by zero.");
  }
  return a / b;
}

}  // namespace demo