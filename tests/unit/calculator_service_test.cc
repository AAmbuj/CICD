#include "calculator/calculator_service.h"

#include <stdexcept>

#include <gtest/gtest.h>

namespace demo::calculator {

TEST(CalculatorServiceTest, AddTwoValues) {
  CalculatorService calculator;
  EXPECT_DOUBLE_EQ(calculator.Add(2.0, 3.0), 5.0);
  EXPECT_DOUBLE_EQ(calculator.Add(-1.0, 1.0), 0.0);
  EXPECT_DOUBLE_EQ(calculator.Add(0.0, 0.0), 0.0);
}

TEST(CalculatorServiceTest, AddThreeValues) {
  CalculatorService calculator;
  EXPECT_DOUBLE_EQ(calculator.Add(1.0, 2.0, 3.0), 6.0);
  EXPECT_DOUBLE_EQ(calculator.Add(-1.0, 0.0, 1.0), 0.0);
}

TEST(CalculatorServiceTest, Subtract) {
  CalculatorService calculator;
  EXPECT_DOUBLE_EQ(calculator.Subtract(10.0, 4.0), 6.0);
  EXPECT_DOUBLE_EQ(calculator.Subtract(0.0, 5.0), -5.0);
}

TEST(CalculatorServiceTest, Multiply) {
  CalculatorService calculator;
  EXPECT_DOUBLE_EQ(calculator.Multiply(3.0, 4.0), 12.0);
  EXPECT_DOUBLE_EQ(calculator.Multiply(-2.0, 5.0), -10.0);
  EXPECT_DOUBLE_EQ(calculator.Multiply(0.0, 100.0), 0.0);
}

TEST(CalculatorServiceTest, Divide) {
  CalculatorService calculator;
  EXPECT_DOUBLE_EQ(calculator.Divide(10.0, 2.0), 5.0);
  EXPECT_DOUBLE_EQ(calculator.Divide(-9.0, 3.0), -3.0);
}

TEST(CalculatorServiceTest, DivideByZeroThrows) {
  CalculatorService calculator;
  EXPECT_THROW(calculator.Divide(1.0, 0.0), std::invalid_argument);
}

}  // namespace demo::calculator