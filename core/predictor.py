from typing import Dict, List, Any, Optional, Tuple


class HRPredictor:
    """
    HR Predictor Class

    This class implements the core algorithm for talent structure prediction,
    including single-year and multi-year forecasting capabilities
    """

    # Define level range constants
    MIN_LEVEL: int = 1
    MAX_LEVEL: int = 7
    LEVEL_RANGE: range = range(MIN_LEVEL, MAX_LEVEL + 1)  # From 1 to 7

    def predict_one_year(
        self,
        current_campus_employees: Dict[int, int],
        current_social_employees: Dict[int, int],
        current_campus_ages: Optional[Dict[int, float]],
        current_social_ages: Optional[Dict[int, float]],
        campus_leaving_ages: Dict[int, float],
        social_leaving_ages: Dict[int, float],
        social_new_hire_ages: Dict[int, float],
        campus_new_hire_age: float,
        campus_promotion_rates: Dict[int, float],
        social_promotion_rates: Dict[int, float],
        campus_attrition_rates: Dict[int, float],
        social_attrition_rates: Dict[int, float],
        hiring_ratios: Dict[int, float],
        campus_ratio: float,
        target_total: int,
        previous_predicted_total_age: Optional[float] = None
    ) -> Tuple[
        Dict[int, int],  # final_campus
        Dict[int, int],  # final_social
        Dict[int, int],  # final_structure
        float,           # predicted_average_level
        float,           # predicted_average_age
        float,           # predicted_campus_ratio
        int,             # campus_hiring
        Dict[int, int],  # social_hiring
        float            # predicted_total_age
    ]:
        """
        Predict personnel structure after one year

        Args:
            current_campus_employees: Current campus recruitment headcount by level
            current_social_employees: Current social recruitment headcount by level
            current_campus_ages: Current average age of campus recruits by level
            current_social_ages: Current average age of social recruits by level
            campus_leaving_ages: Average leaving age of campus recruits
            social_leaving_ages: Average leaving age of social recruits
            social_new_hire_ages: Average age of new social hires
            campus_new_hire_age: Average age of new campus hires
            campus_promotion_rates: Campus recruitment promotion rates
            social_promotion_rates: Social recruitment promotion rates
            campus_attrition_rates: Campus recruitment attrition rates
            social_attrition_rates: Social recruitment attrition rates
            hiring_ratios: Social recruitment distribution ratios
            campus_ratio: Campus recruitment ratio
            target_total: Target total headcount
            previous_predicted_total_age: Total age predicted from previous year

        Returns:
            Tuple containing:
            - final_campus: Predicted campus recruitment headcount
            - final_social: Predicted social recruitment headcount
            - final_structure: Predicted total headcount
            - predicted_average_level: Predicted average level
            - predicted_average_age: Predicted average age
            - predicted_campus_ratio: Predicted campus recruitment ratio
            - campus_hiring: Campus recruitment new hires
            - C: Social recruitment new hires
            - predicted_total_age: Predicted total age
        """
        # Step 1: Calculate promotion adjustments
        A_campus: Dict[int, int] = {}
        A_social: Dict[int, int] = {}

        for level in self.LEVEL_RANGE:
            # Calculate number of employees promoted out
            promoted_out_campus = round(current_campus_employees[level] * campus_promotion_rates[level])
            promoted_out_social = round(current_social_employees[level] * social_promotion_rates[level])

            # Calculate number of employees promoted in from lower level
            promoted_in_campus = round(current_campus_employees[level-1] * campus_promotion_rates[level-1]) if level > self.MIN_LEVEL else 0
            promoted_in_social = round(current_social_employees[level-1] * social_promotion_rates[level-1]) if level > self.MIN_LEVEL else 0

            # Calculate headcount after promotion adjustments
            A_campus[level] = current_campus_employees[level] - promoted_out_campus + promoted_in_campus
            A_social[level] = current_social_employees[level] - promoted_out_social + promoted_in_social

        # Step 2: Calculate attrition adjustments
        B_campus: Dict[int, int] = {
            level: round(A_campus[level] - current_campus_employees[level] * campus_attrition_rates[level])
            for level in self.LEVEL_RANGE
        }

        B_social: Dict[int, int] = {
            level: round(A_social[level] - current_social_employees[level] * social_attrition_rates[level])
            for level in self.LEVEL_RANGE
        }

        B: Dict[int, int] = {
            level: B_campus[level] + B_social[level]
            for level in self.LEVEL_RANGE
        }

        # Step 3: Calculate total hiring needs
        total_B = sum(B.values())
        campus_hiring = round(target_total * campus_ratio)
        total_social_hiring_needed = target_total - total_B - campus_hiring

        # Step 4: Allocate social recruitment hiring slots
        initial_C: Dict[int, int] = {
            level: round(total_social_hiring_needed * hiring_ratios[level])
            for level in self.LEVEL_RANGE
        }

        initial_total = sum(initial_C.values())

        # If rounded total doesn't match target, adjust the level with maximum hiring
        if initial_total != total_social_hiring_needed:
            diff = total_social_hiring_needed - initial_total
            max_hiring_level = max(self.LEVEL_RANGE, key=lambda x: initial_C[x])
            initial_C[max_hiring_level] += diff

        C: Dict[int, int] = {
            level: max(0, initial_C[level])
            for level in self.LEVEL_RANGE
        }

        # Step 5: Projected year-end headcount by level
        final_campus: Dict[int, int] = {
            level: B_campus[level] + (campus_hiring if level == self.MIN_LEVEL else 0)
            for level in self.LEVEL_RANGE
        }

        final_social: Dict[int, int] = {
            level: B_social[level] + C[level]
            for level in self.LEVEL_RANGE
        }

        final_structure: Dict[int, int] = {
            level: final_campus[level] + final_social[level]
            for level in self.LEVEL_RANGE
        }

        # Calculate predicted total headcount
        predicted_total = sum(final_structure.values())

        # Calculate predicted average level
        predicted_average_level = (
            sum(level * final_structure[level] for level in self.LEVEL_RANGE) / predicted_total
            if predicted_total != 0 else 0.0
        )

        # Calculate current total headcount
        current_total = sum(
            current_campus_employees[l] + current_social_employees[l]
            for l in self.LEVEL_RANGE
        )

        # Calculate current total age
        if previous_predicted_total_age is None:
            # Ensure current_campus_ages and current_social_ages are not None
            if current_campus_ages is None or current_social_ages is None:
                raise ValueError("First year prediction requires current campus and social recruitment age data")

            current_total_age = sum(
                current_campus_employees[l] * current_campus_ages[l] +
                current_social_employees[l] * current_social_ages[l]
                for l in self.LEVEL_RANGE
            )
        else:
            current_total_age = previous_predicted_total_age

        # Calculate total attrition headcount and total attrition age
        campus_leaving_total = sum(
            current_campus_employees[level] * campus_attrition_rates[level]
            for level in self.LEVEL_RANGE
        )

        social_leaving_total = sum(
            current_social_employees[level] * social_attrition_rates[level]
            for level in self.LEVEL_RANGE
        )

        campus_leaving_total_age = sum(
            current_campus_employees[level] * campus_attrition_rates[level] * campus_leaving_ages[level]
            for level in self.LEVEL_RANGE
        )

        social_leaving_total_age = sum(
            current_social_employees[level] * social_attrition_rates[level] * social_leaving_ages[level]
            for level in self.LEVEL_RANGE
        )

        # Calculate retained headcount
        survived_total = current_total - (campus_leaving_total + social_leaving_total)

        # Calculate predicted total age
        predicted_total_age = (
            current_total_age -
            (campus_leaving_total_age + social_leaving_total_age) +
            survived_total * 1 +
            campus_hiring * campus_new_hire_age +
            sum(C[level] * social_new_hire_ages[level] for level in self.LEVEL_RANGE)
        )

        # Calculate predicted average age
        predicted_average_age = predicted_total_age / predicted_total if predicted_total != 0 else 0.0

        # Calculate predicted campus recruitment ratio
        predicted_campus_ratio = (
            sum(final_campus[l] for l in self.LEVEL_RANGE) / predicted_total
            if predicted_total > 0 else 0.0
        )

        return (
            final_campus,
            final_social,
            final_structure,
            predicted_average_level,
            predicted_average_age,
            predicted_campus_ratio,
            campus_hiring,
            C,
            predicted_total_age
        )

    def predict_multiple_years(
        self,
        initial_params: Dict[str, Any],
        forecast_years: int
    ) -> List[Dict[str, Any]]:
        """
        Predict multi-year personnel structure changes

        Args:
            initial_params: Dictionary containing all initial parameters
            forecast_years: Number of years to forecast

        Returns:
            List[Dict[str, Any]]: List containing prediction results for each year
        """
        multi_year_results: List[Dict[str, Any]] = []

        # Initialize input data for first year
        current_year_campus = initial_params['current_campus_employees'].copy()
        current_year_social = initial_params['current_social_employees'].copy()
        current_year_campus_ages = initial_params['current_campus_ages'].copy()
        current_year_social_ages = initial_params['current_social_ages'].copy()
        previous_predicted_total_age: Optional[float] = None

        # Loop to predict multiple years
        for year in range(forecast_years):
            result = self.predict_one_year(
                current_year_campus,
                current_year_social,
                current_year_campus_ages if year == 0 else None,
                current_year_social_ages if year == 0 else None,
                initial_params['campus_leaving_ages'],
                initial_params['social_leaving_ages'],
                initial_params['social_new_hire_ages'],
                initial_params['campus_new_hire_age'],
                initial_params['campus_promotion_rates'],
                initial_params['social_promotion_rates'],
                initial_params['campus_attrition_rates'],
                initial_params['social_attrition_rates'],
                initial_params['hiring_ratios'],
                initial_params['campus_ratio'],
                initial_params['target_total'],
                previous_predicted_total_age if year > 0 else None
            )

            # Unpack results
            (
                final_campus,
                final_social,
                final_structure,
                predicted_average_level,
                predicted_average_age,
                predicted_campus_ratio,
                campus_hiring,
                social_hiring,
                predicted_total_age
            ) = result

            # Store current year prediction results
            multi_year_results.append({
                'year': year + 1,
                'current_campus': current_year_campus.copy(),
                'current_social': current_year_social.copy(),
                'final_campus': final_campus,
                'final_social': final_social,
                'final_structure': final_structure,
                'average_level': predicted_average_level,
                'average_age': predicted_average_age,
                'campus_ratio': predicted_campus_ratio,
                'campus_hiring': campus_hiring,
                'social_hiring': social_hiring,
                'total_age': predicted_total_age
            })

            # Update input data for next year
            current_year_campus = final_campus.copy()
            current_year_social = final_social.copy()
            previous_predicted_total_age = predicted_total_age

        return multi_year_results
