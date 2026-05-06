#include "calculator.h"

#include <stdexcept>

#include <gtest/gtest.h>

namespace demo {

TEST(CalculatorTest, AddTwoValues) {
  Calculator calc;
  EXPECT_DOUBLE_EQ(calc.Add(2.0, 3.0), 5.0);
  EXPECT_DOUBLE_EQ(calc.Add(-1.0, 1.0), 0.0);
  EXPECT_DOUBLE_EQ(calc.Add(0.0, 0.0), 0.0);
}

TEST(CalculatorTest, AddThreeValues) {
  Calculator calc;
  EXPECT_DOUBLE_EQ(calc.Add(1.0, 2.0, 3.0), 6.0);
  EXPECT_DOUBLE_EQ(calc.Add(-1.0, 0.0, 1.0), 0.0);
}

TEST(CalculatorTest, Subtract) {
  Calculator calc;
  EXPECT_DOUBLE_EQ(calc.Subtract(10.0, 4.0), 6.0);
  EXPECT_DOUBLE_EQ(calc.Subtract(0.0, 5.0), -5.0);
}

TEST(CalculatorTest, Multiply) {
  Calculator calc;
  EXPECT_DOUBLE_EQ(calc.Multiply(3.0, 4.0), 12.0);
  EXPECT_DOUBLE_EQ(calc.Multiply(-2.0, 5.0), -10.0);
  EXPECT_DOUBLE_EQ(calc.Multiply(0.0, 100.0), 0.0);
}

TEST(CalculatorTest, Divide) {
  Calculator calc;
  EXPECT_DOUBLE_EQ(calc.Divide(10.0, 2.0), 5.0);
  EXPECT_DOUBLE_EQ(calc.Divide(-9.0, 3.0), -3.0);
}

TEST(CalculatorTest, DivideByZeroThrows) {
  Calculator calc;
  EXPECT_THROW(calc.Divide(1.0, 0.0), std::invalid_argument);
}

}  // namespace demo
