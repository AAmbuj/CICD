#ifndef DEMO_CALCULATOR_I_CALCULATOR_SERVICE_H_
#define DEMO_CALCULATOR_I_CALCULATOR_SERVICE_H_

namespace demo::calculator {

class ICalculatorService {
 public:
  virtual ~ICalculatorService() = default;

  virtual double Add(double lhs, double rhs) const = 0;
  virtual double Add(double lhs, double rhs, double extra) const = 0;
  virtual double Subtract(double lhs, double rhs) const = 0;
  virtual double Multiply(double lhs, double rhs) const = 0;
  virtual double Divide(double lhs, double rhs) const = 0;
};

}  // namespace demo::calculator

#endif  // DEMO_CALCULATOR_I_CALCULATOR_SERVICE_H_
