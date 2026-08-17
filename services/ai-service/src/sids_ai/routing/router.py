from sids_ai.schemas.analysis import RoutingResult


def route_problem(crop: str, mode: str) -> RoutingResult:
    # Basic logic: mode determines the routing expectation.
    # In a full system, this would use a lightweight classifier.
    if mode == "QUICK_DIAGNOSIS":
        return RoutingResult(problemType="PEST", confidence=0.85)
    return RoutingResult(problemType="UNKNOWN", confidence=1.0)
