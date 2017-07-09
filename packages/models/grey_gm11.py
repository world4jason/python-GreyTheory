from grey_class import *
import math

class GreyGM11 (GreyClass):

    def __init__(self):
        super(GreyGM11, self).__init__()
        self.forecast_results = []
    
    def __forecast_value(self, x1, a_value, b_value, k):
        return (1 - math.exp(a_value)) * (x1 - (b_value / a_value)) * math.exp(-a_value * k)

    def add_pattern(self, pattern, pattern_key):
        self._add_patterns(pattern, pattern_key)

    def forecast(self, continuous_period = 1):
        self.remove_all_analysis()
        
        ago = self.ago([self.patterns])
        z_boxes = ago[1]
        # Building B matrix, manual transpose z_boxes and add 1.0 to every sub-object.
        factors = []
        for z in z_boxes:
            x_t = []
            # Add negative z
            x_t.append(-z)
            x_t.append(1.0)
            factors.append(x_t)
        
        # Building Y matrix to be output-goals of equations.
        y_vectors = []
        for passed_number in self.patterns[1::]:
            y_vectors.append(passed_number)
        
        solved_equations = self.grey_math.solve_equations(factors, y_vectors)
        # Then, forecasting them at all include next moment value.
        sum_error = 0.0
        x1        = self.patterns[0]
        a_value   = solved_equations[0]
        b_value   = solved_equations[1]
        k         = 1
        length    = len(self.patterns)
        for passed_number in self.patterns[1::]:
            grey_forecast  = GreyForecast()
            forecast_value = self.__forecast_value(x1, a_value, b_value, k)
            self.forecasts.append(forecast_value)

            original_value  = self.patterns[k]
            error_rate      = abs((original_value - forecast_value) / original_value)
            sum_error      += error_rate
            grey_forecast.tag = self._TAG_FORECAST_HISTORY
            grey_forecast.k   = k
            grey_forecast.original_value = original_value
            grey_forecast.forecast_value = forecast_value
            grey_forecast.error_rate     = error_rate

            self.analyzed_results.append(grey_forecast)
            k += 1
        
        # Continuous forecasting next moments.
        if continuous_period > 0:
            for go_head in range(0, continuous_period):
                forecast_value = self.__forecast_value(x1, a_value, b_value, k)
                self.forecasts.append(forecast_value)

                grey_forecast     = GreyForecast()
                grey_forecast.tag = self._TAG_FORECAST_NEXT_MOMENT
                grey_forecast.k   = k # This k means the next moment of forecasted.
                grey_forecast.average_error_rate = sum_error / (length - 1)
                grey_forecast.forecast_value     = forecast_value
                self.analyzed_results.append(grey_forecast)
                k += 1

    def next_moment(self):
        # Last GreyForecast() object is the next moment forecasted.
        return self.analyzed_results[-1].forecast_value

    