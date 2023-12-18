from datetime import datetime
from dbconfig import dynamodb
import uuid


# method for calling all items in any table
def fetchTable(tableName):
    table = dynamodb.Table(tableName)
    res = table.scan()
    items = res['Items']
    return items


# method for getting all saunas in alphabetical order
def fetchSaunas():
    items = fetchTable('sauna')
    saunas = sorted(items, key=lambda x: x.get('name', '').lower())

    for s in saunas:
        s['id'] = int(s['id'])
        s['starttime'] = int(s['starttime'])
        s['endtime'] = int(s['endtime'])

    return saunas


# method for getting all saunas in alphabetical order
def fetchSaunas():
    items = fetchTable('sauna')
    saunas = sorted(items, key=lambda x: x.get('name', '').lower())

    for s in saunas:
        s['id'] = int(s['id'])
        s['starttime'] = int(s['starttime'])
        s['endtime'] = int(s['endtime'])

    return saunas


# method for getting all saunas in alphabetical order
def fetchReservations(saunaId):
    table = dynamodb.Table('reservation')

    response = table.scan(
        FilterExpression='saunaid = :saunaid',
        ExpressionAttributeValues={
            ':saunaid': saunaId,
        }
    )

    reservations = response['Items']

    for r in reservations:
        r['saunaid'] = int(r['saunaid'])
        r['userid'] = int(r['userid'])

    return reservations


# fetch user by name
def fetchUser(name):
    table = dynamodb.Table('user')
    users = table.scan()

    for u in users['Items']:
        if u['username'] == name:
            return u

    return None


# fetch user by id
def fetchUserById(id):
    table = dynamodb.Table('user')

    response = table.scan(
        FilterExpression='id = :id',
        ExpressionAttributeValues={
            ':id': id,
        }
    )

    users = response['Items']

    if len(users) < 1:
        return None
    
    return users[0]


# fetch user's tokens
def fetchUserTokensCount(userid):
    MAX_TOKENS = 5

    table = dynamodb.Table('reservation')

    response = table.scan(
        FilterExpression='userid = :id',
        ExpressionAttributeValues={
            ':id': int(userid),
        }
    )

    reservationsByUser = response['Items']

    return MAX_TOKENS - len(reservationsByUser)


def createReservation(saunaId, userId, date):
    # if creation process of reservation item doesn't have errors,
    # assume it to be successful. Otherwise return False as an
    # indicator of errors
    try:
        table = dynamodb.Table('reservation')

        resItem = {
            'id': str(uuid.uuid4()),
            'saunaid': int(saunaId),
            'userid': int(userId),
            'time': date,
        }

        table.put_item(Item=resItem)

        return True
    except:
        return False


def cancelReservation(saunaid, resid):
    # if deleting process of reservation item doesn't have errors,
    # assume it to be successful. Otherwise return False as an
    # indicator of errors
    try:
        table = dynamodb.Table('reservation')

        response = table.delete_item(
            Key={
                'saunaid': int(saunaid),
                'id': resid
            }
        )

        return True
    except:
        return False
    

# method for deleting multiple reservations
def deleteMultipleReservations(reservations):
    try:
        table = dynamodb.Table('reservation')

        with table.batch_writer() as batch:
            for r in reservations:
                batch.delete_item(
                    Key={
                        'saunaid': int(r.get('saunaid')),
                        'id': r.get('id')
                    }
                )
        return True
    except:
        return False
    

def deleteOldReservations():
    saunas = fetchSaunas()
    saunaIds = [s.get('id') for s in saunas]

    oldReservs = []
    # fetch all reservations in one list
    for s in saunaIds:
        reservs = fetchOldReservations(s)
        if len(reservs) > 0:
            oldReservs.extend(reservs)

    # if old reservations are found, delete them 
    if len(oldReservs) > 0:
        deleteMultipleReservations(oldReservs)
    

# fetch old reservations from sauna
def fetchOldReservations(saunaId):
    table = dynamodb.Table('reservation')

    current_time = datetime.utcnow()
    current_timestamp = current_time.strftime('%Y-%m-%dT%H')

    response = table.query(
        KeyConditionExpression='saunaid = :saunaid',
        FilterExpression='#timestamp < :current_timestamp',
        ExpressionAttributeNames={'#timestamp': 'time'},
        ExpressionAttributeValues={
            ':saunaid': int(saunaId),
            ':current_timestamp': current_timestamp
        }
    )

    old_reservations = response['Items']

    return old_reservations
