import random
import time

class ModelInferenceEngine:
    def __init__(self, model_registry):
        self.model_registry = model_registry
        self.api_clients = {}
        
    def evaluate_model(self, model_id, test_cases, use_case_requirements):
        model_info = self.model_registry.get_model(model_id)
        if not model_info:
            return None
        
        results = []
        total_cost = 0
        total_time = 0
        
        for test_case in test_cases:
            start_time = time.time()
            response = self._call_model_api(model_id, test_case["prompt"], use_case_requirements)
            end_time = time.time()
            response_time = end_time - start_time
            
            cost = self._calculate_cost(model_info, response["input_tokens"], response["output_tokens"])
            total_cost += cost
            total_time += response_time
            
            evaluation_scores = self._evaluate_response(test_case, response["content"], use_case_requirements)
            
            results.append({
                "test_case_id": test_case["id"],
                "test_case_type": test_case["type"],
                "response": response["content"],
                "response_time": response_time,
                "cost": cost,
                "input_tokens": response["input_tokens"],
                "output_tokens": response["output_tokens"],
                "evaluation_scores": evaluation_scores
            })
        
        aggregate_metrics = self._calculate_aggregate_metrics(results)
        aggregate_metrics["total_cost"] = total_cost
        aggregate_metrics["total_time"] = total_time
        if len(test_cases) > 0:
            aggregate_metrics["avg_response_time"] = total_time / len(test_cases)
        else:
            aggregate_metrics["avg_response_time"] = 0.0
            aggregate_metrics.setdefault("accuracy", 0.0)
            aggregate_metrics.setdefault("total_cost", total_cost)
            aggregate_metrics.setdefault("total_time", total_time)
        
        return {
            "model_id": model_id,
            "model_info": model_info,
            "test_results": results,
            "aggregate_metrics": aggregate_metrics
        }
    
    def _call_model_api(self, model_id, prompt, use_case_requirements):
        return {
            "content": f"Simulated response from {model_id} to: {prompt}",
            "input_tokens": len(prompt.split()) * 1.33,
            "output_tokens": random.randint(50, 200)
        }
    
    def _calculate_cost(self, model_info, input_tokens, output_tokens):
        input_cost = (input_tokens / 1000) * model_info["api_cost_input"]
        output_cost = (output_tokens / 1000) * model_info["api_cost_output"]
        return input_cost + output_cost
    
    def _evaluate_response(self, test_case, response, use_case_requirements):
        evaluation_criteria = test_case["evaluation_criteria"]
        scores = {}
        
        for criterion in evaluation_criteria:
            if criterion == "logical_consistency":
                scores[criterion] = self._evaluate_logical_consistency(response)
            elif criterion == "correctness":
                scores[criterion] = self._evaluate_correctness(response, test_case)
            elif criterion == "originality":
                scores[criterion] = self._evaluate_originality(response)
        
        return scores
    
    def _evaluate_logical_consistency(self, response):
        return random.uniform(0.7, 1.0)
    
    def _evaluate_correctness(self, response, test_case):
        return random.uniform(0.8, 1.0)
    
    def _evaluate_originality(self, response):
        return random.uniform(0.6, 1.0)
    
    def _calculate_aggregate_metrics(self, results):
        avg_scores = {}
        score_counts = {}
        
        for result in results:
            for criterion, score in result["evaluation_scores"].items():
                if criterion not in avg_scores:
                    avg_scores[criterion] = 0
                    score_counts[criterion] = 0
                avg_scores[criterion] += score
                score_counts[criterion] += 1
        
        for criterion in avg_scores:
            avg_scores[criterion] /= score_counts[criterion]
        
        return avg_scores
