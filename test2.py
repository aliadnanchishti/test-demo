from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
import joblib
import os
import pandas as pd
from azureml.core import Run, Datastore, Model, Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
import argparse
from dotenv import load_dotenv
load_dotenv()
#ws = Run.get_context()

parser = argparse.ArgumentParser()
parser.add_argument("--ws",
                    dest="ws",
                    )

parser.add_argument("--rg",
                    dest="rg",
                    )

parser.add_argument("--datastore",
                    dest="datastore",
                    )

parser.add_argument("--dataset",
                    dest="dataset",
                    )

args = parser.parse_args()


ws = Workspace.get(args.ws, ServicePrincipalAuthentication(
    tenant_id=os.getenv('tenant_id'),
    service_principal_id=os.getenv('service_principal_id'),
    service_principal_password=os.getenv('service_principal_password')
), 
    subscription_id=os.getenv('subscription_id'),
    resource_group=args.rg
)

ds = Datastore.get(ws, args.datastore)

ds.download("assets", args.dataset, overwrite=False)


# Load dataset
url = "assets/"+args.dataset
names = ['sepal-length', 'sepal-width', 'petal-length', 'petal-width', 'class']
dataset = read_csv(url, names=names)

# Split-out validation dataset
array = dataset.values
X = array[:,0:4]
y = array[:,4]
X_train, X_validation, Y_train, Y_validation = train_test_split(X, y, test_size=0.20, random_state=1)
# Make predictions on validation dataset
model = SVC(gamma='auto')
model.fit(X_train, Y_train)
predictions = model.predict(X_validation)
# Evaluate predictions
print(accuracy_score(Y_validation, predictions))
print(confusion_matrix(Y_validation, predictions))
print(classification_report(Y_validation, predictions))


joblib.dump(model, "trained_model1.pkl")

Model.register(ws, "trained_model1.pkl", "new_model")
