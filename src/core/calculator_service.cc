#include "calculator/calculator_service.h"

#include "calculator/operations/arithmetic_operations.h"

namespace demo::calculator {

double CalculatorService::Add(double lhs, double rhs) const {
  return ops::Add(lhs, rhs);
}

double CalculatorService::Add(double lhs, double rhs, double extra) const {
  return ops::Add(lhs, rhs, extra);
}

double CalculatorService::Subtract(double lhs, double rhs) const {
  return ops::Subtract(lhs, rhs);
}

double CalculatorService::Multiply(double lhs, double rhs) const {
  return ops::Multiply(lhs, rhs);
}

double CalculatorService::Divide(double lhs, double rhs) const {
  return ops::Divide(lhs, rhs);
}

}  // namespace demo::calculator