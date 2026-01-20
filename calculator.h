#ifndef SRC_CALCULATOR_H_
#define SRC_CALCULATOR_H_

namespace demo {

class Calculator {
 public:
  Calculator() = default;
  ~Calculator() = default;

  double Add(double a, double b);
  double Subtract(double a, double b);
  double Multiply(double a, double b);
  double Divide(double a, double b);
};

}  // namespace demo

#endif  // SRC_CALCULATOR_H_