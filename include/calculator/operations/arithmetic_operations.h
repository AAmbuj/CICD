#ifndef DEMO_CALCULATOR_OPERATIONS_ARITHMETIC_OPERATIONS_H_
#define DEMO_CALCULATOR_OPERATIONS_ARITHMETIC_OPERATIONS_H_

namespace demo::calculator::ops {

double Add(double lhs, double rhs);
double Add(double lhs, double rhs, double extra);
double Subtract(double lhs, double rhs);
double Multiply(double lhs, double rhs);
double Divide(double lhs, double rhs);

}  // namespace demo::calculator::ops

#endif  // DEMO_CALCULATOR_OPERATIONS_ARITHMETIC_OPERATIONS_H_