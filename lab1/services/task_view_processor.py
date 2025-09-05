from lab1.services.assignment_manager import AssignmentManager


class TaskViewProcessor:
    @staticmethod
    def process_task1(probability):
        manager = AssignmentManager()
        freq, theory = manager.run_task1(probability)
        return {
            'frequency': round(freq, 4),
            'theory': round(theory, 4)
        }

    @staticmethod
    def process_task2(probabilities):
        manager = AssignmentManager()
        freqs, theories = manager.run_task2(probabilities)

        task2_table_data = []
        freqs_rounded = [round(f, 4) for f in freqs]
        theories_rounded = [round(t, 4) for t in theories]
        for i in range(len(freqs_rounded)):
            task2_table_data.append({
                'event': i + 1,
                'frequency': freqs_rounded[i],
                'theory': theories_rounded[i]
            })
        return task2_table_data
