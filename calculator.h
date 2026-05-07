#ifndef CALCULATOR_H_
#define CALCULATOR_H_

namespace demo {

class Calculator {
 public:
  Calculator() = default;
  ~Calculator() = default;

  double Add(double a, double b);
  double Add(double a, double b, double c);
  double Subtract(double a, double b);
  double Multiply(double a, double b);
  double Divide(double a, double b);
};

}  // namespace demo

#endif  // CALCULATOR_H_