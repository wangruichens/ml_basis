# Auther        : wangrc
# Date          : 2019-01-29
# Description   :
# Refers        :
# Returns       :

import numpy as np
import pandas as pd

dataset = pd.read_csv('../data/train.csv')
X_test = pd.read_csv('../data/test.csv')

dataset_title = [i.split(',')[1].split('.')[0].strip() for i in dataset['Name']]
dataset['Title'] = pd.Series(dataset_title)
dataset['Title'] = dataset['Title'].replace(
    ['Lady', 'the Countess', 'Countess', 'Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona', 'Ms',
     'Mme', 'Mlle'], 'Rare')


dataset_title = [i.split(',')[1].split('.')[0].strip() for i in X_test['Name']]
X_test['Title'] = pd.Series(dataset_title)
X_test['Title'].value_counts()
X_test['Title'] = X_test['Title'].replace(['Lady', 'the Countess', 'Countess', 'Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona', 'Ms', 'Mme', 'Mlle'], 'Rare')

dataset['FamilyS'] = dataset['SibSp'] + dataset['Parch'] + 1
X_test['FamilyS'] = X_test['SibSp'] + X_test['Parch'] + 1


def family(x):
    if x < 2:
        return 'Single'
    elif x == 2:
        return 'Couple'
    elif x <= 4:
        return 'InterM'
    else:
        return 'Large'


dataset['FamilyS'] = dataset['FamilyS'].apply(family)
X_test['FamilyS'] = X_test['FamilyS'].apply(family)

dataset['Embarked'].fillna(dataset['Embarked'].mode()[0], inplace=True)
X_test['Embarked'].fillna(X_test['Embarked'].mode()[0], inplace=True)
dataset['Age'].fillna(dataset['Age'].median(), inplace=True)
X_test['Age'].fillna(X_test['Age'].median(), inplace=True)
X_test['Fare'].fillna(X_test['Fare'].median(), inplace=True)

dataset = dataset.drop(['PassengerId', 'Cabin', 'Name', 'SibSp', 'Parch', 'Ticket'], axis=1)
X_test_passengers = X_test['PassengerId']
X_test = X_test.drop(['PassengerId', 'Cabin', 'Name', 'SibSp', 'Parch', 'Ticket'], axis=1)

X_train = dataset.iloc[:, 1:9].values
Y_train = dataset.iloc[:, 0].values
X_test = X_test.values

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
labelencoder_X_1 = LabelEncoder()
X_train[:, 1] = labelencoder_X_1.fit_transform(X_train[:, 1])
X_train[:, 4] = labelencoder_X_1.fit_transform(X_train[:, 4])
X_train[:, 5] = labelencoder_X_1.fit_transform(X_train[:, 5])
X_train[:, 6] = labelencoder_X_1.fit_transform(X_train[:, 6])

labelencoder_X_2 = LabelEncoder()
X_test[:, 1] = labelencoder_X_2.fit_transform(X_test[:, 1])
X_test[:, 4] = labelencoder_X_2.fit_transform(X_test[:, 4])
X_test[:, 5] = labelencoder_X_2.fit_transform(X_test[:, 5])
X_test[:, 6] = labelencoder_X_2.fit_transform(X_test[:, 6])

one_hot_encoder = OneHotEncoder(categorical_features = [0, 1, 4, 5, 6])
X_train = one_hot_encoder.fit_transform(X_train).toarray()
X_test = one_hot_encoder.fit_transform(X_test).toarray()

from sklearn.model_selection import train_test_split

x_train, x_val, y_train, y_val = train_test_split(X_train, Y_train, test_size = 0.1)

import torch
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(19, 2)
        # self.fc2 = nn.Linear(32, 2)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = F.dropout(x, p=0.1)
        # x = self.fc2(x)
        x = F.sigmoid(x)

        return x


net = Net()

batch_size = 50
num_epochs = 50
learning_rate = 0.01
batch_no = len(x_train) // batch_size

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(net.parameters(), lr=learning_rate)

from sklearn.utils import shuffle
from torch.autograd import Variable

for epoch in range(num_epochs):
    if epoch % 5 == 0:
        print('Epoch {}'.format(epoch+1))
    x_train, y_train = shuffle(x_train, y_train)
    # Mini batch learning
    for i in range(batch_no):
        start = i * batch_size
        end = start + batch_size
        x_var = torch.FloatTensor(x_train[start:end])
        y_var = torch.LongTensor(y_train[start:end])
        # Forward + Backward + Optimize
        optimizer.zero_grad()
        ypred_var = net(x_var)
        loss =criterion(ypred_var, y_var)
        loss.backward()
        optimizer.step()
# Evaluate the model
test_var = torch.FloatTensor(x_val)
with torch.no_grad():
    result = net(test_var)
_, labels = torch.max(result, 1)
num_right = np.sum(labels.data.numpy() == y_val)
print('Accuracy {:.2f}'.format(num_right / len(y_val)))

# Applying model on the test data
X_test_var = torch.FloatTensor(X_test)
with torch.no_grad():
    test_result = net(X_test_var)
_, labels = torch.max(test_result, 1)
survived = labels.data.numpy()

import csv

submission = [['PassengerId', 'Survived']]
for i in range(len(survived)):
    submission.append([X_test_passengers[i], survived[i]])

with open('../data/submission.csv', 'w') as submissionFile:
    writer = csv.writer(submissionFile)
    writer.writerows(submission)

print('Writing Complete!')