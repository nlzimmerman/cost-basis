#!/bin/bash

docker run -it -v $(pwd)/notebooks:/notebooks -v $(pwd)/python:/python -e "PYTHONPATH=/python" -p 8888:8888 cost-basis
