""" Step 1 Measuring Execution Time (without and with CUDA) """
import time
from speech_to_speech import *


# start the version of script running regularly
start_time = time.time()

main()

end_time = time.time()
execution_time_cpu = end_time - start_time
print(f"execution time (with CPU alone): {execution_time_cpu} seconds")

# just CPU above
