#ifndef CALCULATOR_H_
#define CALCULATOR_H_

#include "calculator/calculator_service.h"

namespace demo {

// Backward-compatible alias for existing callers that include "calculator.h".
using Calculator = calculator::CalculatorService;

}  // namespace demo

#endif  // CALCULATOR_H_