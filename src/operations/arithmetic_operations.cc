#include "calculator/operations/arithmetic_operations.h"

#include <cmath>
#include <stdexcept>

namespace demo::calculator::ops {

double Add(double lhs, double rhs) {
  return lhs + rhs;
}

double Add(double lhs, double rhs, double extra) {
  return lhs + rhs + extra;
}

double Subtract(double lhs, double rhs) {
  return lhs - rhs;
}

double Multiply(double lhs, double rhs) {
  return lhs * rhs;
}

double Divide(double lhs, double rhs) {
  if (std::fpclassify(rhs) == FP_ZERO) {
    throw std::invalid_argument("Cannot divide by zero.");
  }
  return lhs / rhs;
}

}  // namespace demo::calculator::ops