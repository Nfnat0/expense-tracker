from flask import Flask, request, jsonify
import boto3
import os
import uuid
import awsgi

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


@app.route('/expenses', methods=['GET'])
def get_expenses():
    response = table.scan()
    return jsonify(response['Items'])


@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    expense_id = str(uuid.uuid4())
    item = {
        'expenseId': expense_id,
        'description': data['description'],
        'amount': data['amount'],
        'date': data['date'],
        'label': data.get('label', 'default')  # Add label to the item
    }
    table.put_item(Item=item)
    return jsonify(item), 201


@app.route('/expenses/<expenseId>', methods=['PUT'])
def update_expense(expenseId):
    data = request.json
    update_expression = "SET description = :description, amount = :amount, #date = :date, label = :label"
    expression_attribute_values = {
        ':description': data['description'],
        ':amount': data['amount'],
        ':date': data['date'],
        ':label': data.get('label', 'default')
    }
    expression_attribute_names = {
        '#date': 'date'
    }
    table.update_item(
        Key={'expenseId': expenseId},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names
    )
    return jsonify({'expenseId': expenseId, 'message': 'Expense updated successfully'})


@app.route('/expenses/<expenseId>', methods=['DELETE'])
def delete_expense(expenseId):
    table.delete_item(Key={'expenseId': expenseId})
    return '', 204


def lambda_handler(event, context):
    return awsgi.response(app, event, context)  
