import astar
import message

class ARA:
    @staticmethod
    def search_map(map, heuristic, time_limit, epsilon=5.0, message_queue=None):
        delta_epsilon = 0.5
        # Run path finding
        search_result = astar.AStar.search_map(map, heuristic, epsilon, message_queue)
        _, correct_path = astar.AStar.parse_result(*search_result, message_queue)
        # Get running time
        run_time = astar.AStar.search_map.time_elapsed
        if message_queue != None:
            message_queue.put_nowait(message.Message(action="ARA_INFO", param=(epsilon, len(correct_path), run_time)))
        # Check if time_limit is satisfied or not
        limit_satisfied = run_time < time_limit


        while run_time < time_limit and epsilon > 1.0 and delta_epsilon >= 0.1:
            # Search with temporary epsilon
            temp_epsilon = epsilon - delta_epsilon
            # If decreasing epsilon make it smaller than 1.0
            # decrease delta epsilon
            # and continue
            if temp_epsilon <= 1.0:
                delta_epsilon /= 2.0
                continue

            search_result = astar.AStar.search_map(map, heuristic, epsilon, message_queue)
            _, correct_path = astar.AStar.parse_result(*search_result, message_queue)
            # Get running time
            temp_time = astar.AStar.search_map.time_elapsed
            

            # If temporary running time is acceptable
            # update run_time and epsilon
            if temp_time < time_limit and temp_epsilon >= 1.0:
                run_time = temp_time
                epsilon = temp_epsilon
                print("epsilon: ",epsilon)
                if message_queue != None:
                    msg = message.Message(action="ARA_INFO")
                    msg.param = (temp_epsilon, len(correct_path), temp_time)
                    message_queue.put_nowait(msg)
            # Else
            # decrease delta epsilon
            else:
                delta_epsilon /= 2.0
        
        if message_queue != None:
            message_queue.put_nowait(message.Message(action="ARA_UNLOCK"))
        return run_time, epsilon, limit_satisfied