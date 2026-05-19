#ifndef DEMO_CALCULATOR_CALCULATOR_SERVICE_H_
#define DEMO_CALCULATOR_CALCULATOR_SERVICE_H_

#include "calculator/i_calculator_service.h"

namespace demo::calculator {

class CalculatorService : public ICalculatorService {
 public:
  double Add(double lhs, double rhs) const override;
  double Add(double lhs, double rhs, double extra) const override;
  double Subtract(double lhs, double rhs) const override;
  double Multiply(double lhs, double rhs) const override;
  double Divide(double lhs, double rhs) const override;
};

}  // namespace demo::calculator

#endif  // DEMO_CALCULATOR_CALCULATOR_SERVICE_H_
