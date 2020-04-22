#Example: scikit-learn and Swagger
import json
import numpy as np
import os
from sklearn.externals import joblib
from sklearn.linear_model import Ridge
from azureml.core import Model

from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType


def init():
    global model

    path = 'azureml-models/'
    files = []

    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))

    for f in files:
        loaded = joblib.load(f)
        if hasattr(loaded, "fit") and model is None:
            model = loaded
            print("Model found", model)
            continue
        if hasattr(loaded, "tolist") and encoded_columns is None:
            encoded_columns = loaded
            print("Model_ec found: ", len(encoded_columns))
            continue

    #model_path = Model.get_model_path('new_model')

    #model = joblib.load(model_path)


input_sample = np.array([[10, 9, 8, 7]])
output_sample = np.array([3726.995])


@input_schema('data', NumpyParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data):
    try:
        #data = json.loads(request)
        result = model.predict(data)
        # You can return any data type, as long as it is JSON serializable.
        return result.tolist()
    except Exception as e:
        error = str(e)
        return error,data