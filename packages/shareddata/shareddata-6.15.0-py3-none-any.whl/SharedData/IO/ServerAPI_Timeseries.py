# Import all common variables, functions, and the Flask app
from SharedData.IO.ServerAPI_Common import *

@app.route('/api/timeseries', methods=['GET'])
def list_timeseries():
    """
    Endpoint to list all timeseries.
    Query params:
        - keyword: (optional) a keyword to filter timeseries names.
        - user: (optional) user name, default 'master'.
    Response: JSON list of timeseries names and info.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        keyword = request.args.get('keyword', '')
        user = request.args.get('user', 'master')
        
        # Get timeseries list from SharedData
        timeseries_df = shdata.list_timeseries(keyword=keyword, user=user)
        
        if len(timeseries_df) == 0:
            return Response(status=204)
        
        # Convert DataFrame to list of dictionaries for JSON serialization
        timeseries_list = timeseries_df.reset_index().to_dict('records')
        
        # Clean up datetime serialization for JSON
        for ts in timeseries_list:
            for key, value in ts.items():
                if pd.isna(value):
                    ts[key] = None
                elif isinstance(value, pd.Timestamp):
                    ts[key] = value.isoformat()
        
        response_data = json.dumps(timeseries_list).encode('utf-8')
        response = Response(response_data, mimetype='application/json')
        response.headers['Content-Length'] = len(response_data)
        return response
    except Exception as e:        
        error_data = json.dumps({'error': str(e).replace('\n', ' ')}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
        response.headers['Error-Message'] = error_data
        return response

@app.route('/api/timeseries/<database>/<period>/<source>', methods=['POST'])
def create_timeseries_source(database, period, source):
    """
    Create a timeseries container for a given database, period, and source.
    
    This endpoint creates a new timeseries container similar to calling shdata.timeseries() directly.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The period identifier (D1, M15, M1, etc.).
    - source (str): The source identifier.
    
    Query Parameters:
    - user (str, optional): User identifier, defaults to 'master'.
    - startdate (str, optional): Start date for the timeseries in ISO format.
    - columns (str, optional): Comma-separated list of column names.
    
    Returns:
    - JSON response with creation status.
    - 401 Unauthorized if authentication fails.
    - 500 Internal Server Error with error details if an exception occurs.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        
        user = request.args.get('user', 'master')
        startdate = request.args.get('startdate')        
        
        # Parse optional parameters
        startdate_obj = None
        if startdate:
            startdate_obj = pd.Timestamp(startdate)
                    
        # Create timeseries container using shdata interface
        shdata.timeseries(database, period, source, 
                                       user=user, 
                                       startDate=startdate_obj)
        
        response_data = json.dumps({
            'status': 'success', 
            'message': 'Timeseries container created',
            'database': database,
            'period': period,
            'source': source,
            'user': user
        }).encode('utf-8')
        
        response = Response(response_data, status=201, mimetype='application/json')
        response.headers['Content-Length'] = str(len(response_data))
        return response
        
    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

@app.route('/api/timeseries/<database>/<period>/<source>/write', methods=['PATCH'])
def write_timeseries_source(database: str, period: str, source: str):
    """
    Triggers a write operation for all timeseries in a source container.
    
    This endpoint calls the underlying timeseries container's write() method to flush
    all data to persistent storage for the entire source.
    
    Parameters:
        database (str): The name of the database.
        period (str): The time period associated with the timeseries.
        source (str): The source identifier of the timeseries.
    
    Optional Query Parameters:
        user (str): The user performing the write operation; defaults to 'master' if not provided.
        startdate (str): Optional start date for the write operation in ISO format.
    
    Returns:
        flask.Response: HTTP 200 OK if write is successful with operation details,
                        HTTP 404 Not Found if the timeseries source does not exist,
                        HTTP 500 Internal Server Error if write operation fails.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
            
        user = request.args.get('user', 'master')
        startdate = request.args.get('startdate')

        
        # Parse optional startdate parameter
        startdate_obj = None
        if startdate is not None:
            startdate_obj = pd.Timestamp(startdate)
        
        
        ts = shdata.timeseries(database, period, source, user=user, startDate=startdate)
        ts.write(startDate=startdate_obj)
        
        response_data = json.dumps({
            'status': 'success',
            'message': 'Timeseries source write operation completed',
            'database': database,
            'period': period,
            'source': source,
            'user': user,
            'startdate': startdate
        }).encode('utf-8')
        
        response = Response(response_data, status=200, mimetype='application/json')
        response.headers['Content-Length'] = str(len(response_data))
        return response
        
    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

@app.route('/api/timeseries/<database>/<period>/<source>', methods=['DELETE'])
def delete_timeseries_source(database, period, source):
    """
    Delete all timeseries for a given database, period, and source.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The period identifier (D1, M15, M1, etc.).
    - source (str): The source identifier.
    
    Returns:
    - JSON response with the result of the deletion operation.
    - 401 Unauthorized if authentication fails.
    - 500 Internal Server Error with error details if an exception occurs.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        
        user = request.args.get('user', 'master')
        
        # Use shdata.delete_timeseries for deletion at source level
        success = shdata.delete_timeseries(database, period, source, user=user)
        
        if success:
            return Response(status=204)
        else:
            return Response(status=404)
            
    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        response = Response(status=500)                
        response.headers['Error-Message'] = str(e).replace('\n', ' ')
        return response

@app.route('/api/timeseries/<database>/<period>/<source>/<tag>', methods=['HEAD','GET', 'POST', 'DELETE', 'PATCH'])
@swag_from(docspath)
def timeseries(database, period, source, tag):
    """
    Handle CRUD operations on a specified timeseries within a database.
    
    This endpoint supports GET, POST, DELETE, HEAD, and PATCH HTTP methods to interact with a timeseries identified by the given database, period, source, and tag parameters.
    
    Authentication is required for all requests. If authentication fails, a 401 Unauthorized response is returned.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The period identifier (D1, M15, M1, etc.).
    - source (str): The source identifier.
    - tag (str): The name of the timeseries tag.
    
    Returns:
    - JSON response with the result of the requested operation.
    - 401 Unauthorized if authentication fails.
    - 405 Method Not Allowed if the HTTP method is not supported.
    - 500 Internal Server Error with error details if an exception occurs.
    """
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        
        if request.method == 'HEAD':
            return head_timeseries(database, period, source, tag, request)
        elif request.method == 'GET':
            return get_timeseries(database, period, source, tag, request)
        elif request.method == 'POST':
            return post_timeseries(database, period, source, tag, request)
        elif request.method == 'DELETE':
            return delete_timeseries(database, period, source, tag, request)
        elif request.method == 'PATCH':
            return write_timeseries(database, period, source, tag, request)
        else:
            return jsonify({'error': 'method not allowed'}), 405
        
    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        response = Response(status=500)                
        response.headers['Error-Message'] = str(e).replace('\n', ' ')
        return response

def head_timeseries(database: str, period: str, source: str, tag: str, request):
    """
    Respond to HTTP HEAD requests with metadata headers for a given timeseries.
    Returns information about the timeseries structure and size.
    """
    tagsubfolder = request.args.get('tagsubfolder')  # Optional
    user = request.args.get('user', 'master')
    
    if tagsubfolder is not None:
        tag = tag + '/' + tagsubfolder
    
    try:
        # Get timeseries data to extract metadata
        ts_data = shdata.timeseries(database, period, source, tag, user=user)
        
        if ts_data is None or len(ts_data) == 0:
            return Response(status=404)
        
        response = Response(status=200)
        response.headers["Timeseries-Columns"] = ",".join(ts_data.columns.tolist())
        response.headers["Timeseries-Start"] = ts_data.index.min().isoformat()
        response.headers["Timeseries-End"] = ts_data.index.max().isoformat()
        response.headers["Timeseries-Count"] = str(len(ts_data))
        response.headers["Timeseries-Period"] = period
        return response
        
    except Exception as e:
        return Response(status=404)

def get_timeseries(database: str, period: str, source: str, tag: str, request):
    """
    Retrieve and return a timeseries from the specified database with filtering, sorting, and formatting options.
    
    Parameters:
    - database (str): The name of the database to query.
    - period (str): The period or partition of the database.
    - source (str): The data source identifier.
    - tag (str): The name of the timeseries tag to query.
    - request (flask.Request): The Flask request object containing query parameters and headers.
    
    Query Parameters (via request.args):
    - tagsubfolder (str, optional): Subfolder appended to the tag.
    - user (str, optional): User identifier for access control, defaults to 'master'.
    - startdate (str, optional): Start date filter in ISO format.
    - enddate (str, optional): End date filter in ISO format.
    - columns (str, optional): Comma-separated list of columns to include.
    - format (str, optional): Output format, one of 'json' (default), 'csv', or 'bin'.
    - dropna (str, optional): Whether to drop NaN rows, defaults to 'True'.
    """
    tagsubfolder = request.args.get('tagsubfolder')  # Optional
    user = request.args.get('user', 'master')
    startdate = request.args.get('startdate')
    enddate = request.args.get('enddate')
    columns = request.args.get('columns')
    output_format = request.args.get('format', 'bin').lower()
    dropna = request.args.get('dropna', 'True').lower() == 'true'
    accept_encoding = request.headers.get('Accept-Encoding', '')
    
    if tagsubfolder is not None:
        tag = tag + '/' + tagsubfolder
    
    try:
        
        ts_data = shdata.timeseries(database,period,source,tag,user=user)
        
        # Apply date filtering - create a copy to avoid modifying original data
        if startdate is not None:
            startdate = pd.Timestamp(startdate)
            ts_data = ts_data.loc[startdate:].copy()
            
        if enddate is not None:
            enddate = pd.Timestamp(enddate)
            ts_data = ts_data.loc[:enddate].copy()
            
        # Apply column filtering
        if columns is not None:
            columns_list = [s.strip() for s in columns.split(',')]
            # Filter to only existing columns
            columns_list = [s for s in columns_list if s in ts_data.columns]
            if columns_list:
                ts_data = ts_data[columns_list].copy()
        
        # Drop rows that are all NaN (optional)
        if dropna:
            ts_data = ts_data.dropna(how='all')
        
        if len(ts_data) == 0:
            return Response(status=204)
        
        # Return data in requested format
        if output_format == 'csv':
            csv_data = ts_data.to_csv()
            if 'gzip' in accept_encoding:
                response_csv = csv_data.encode('utf-8')
                response_compressed = gzip.compress(response_csv, compresslevel=1)
                response = Response(response_compressed, mimetype='text/csv')
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(response_compressed)
                return response
            else:
                response_data = csv_data.encode('utf-8')
                response = Response(response_data, mimetype='text/csv')
                response.headers['Content-Length'] = len(response_data)
                return response
                
        elif output_format == 'bin':
            # Return binary format similar to tables
            bson_payload = {
                'index': ts_data.index.astype(np.int64).values.tobytes(),
                'columns': ts_data.columns.tolist(),
                'data': ts_data.values.astype(np.float64).tobytes(),
                'shape': ts_data.shape
            }
            bson_data = bson.encode(bson_payload)
            compressed = lz4f.compress(bson_data)
            
            response = Response(compressed, mimetype='application/octet-stream')
            response.headers['Content-Encoding'] = 'lz4'
            response.headers['Content-Length'] = len(compressed)
            return response
            
        else:  # JSON format
            # Reset index to include datetime in JSON
            ts_json = ts_data.reset_index()
            ts_json['date'] = ts_json['date'].dt.isoformat()
            
            response_data = {
                'tag': tag,
                'period': period,
                'total': len(ts_data),
                'data': ts_json.to_dict(orient='records')
            }
            
            if 'gzip' in accept_encoding:
                response_json = json.dumps(response_data).encode('utf-8')
                response_compressed = gzip.compress(response_json, compresslevel=1)
                response = Response(response_compressed, mimetype='application/json')
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(response_compressed)
                return response
            else:
                response_json = json.dumps(response_data).encode('utf-8')
                response = Response(response_json, mimetype='application/json')
                response.headers['Content-Length'] = len(response_json)
                return response
                
    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

def post_timeseries(database: str, period: str, source: str, tag: str, request):
    """
    Handle a POST request to insert or update timeseries data.
    
    Parameters:
    - database (str): The name of the database.
    - period (str): The period identifier.
    - source (str): The data source identifier.
    - tag (str): The timeseries tag name.
    - request (flask.Request): The incoming HTTP request object containing query parameters, headers, and data.
    
    Behavior:
    1. Parses optional query parameters:
       - 'tagsubfolder' to append a subfolder to the tag name.
       - 'user' with a default value of 'master'.
       - 'columns' to specify the column names for the timeseries.
       - 'overwrite' indicating whether to overwrite existing data (default False).
    2. Handles input data which can be either:
       - lz4 compressed BSON binary data (with 'Content-Encoding' header set to 'lz4'), or
       - JSON formatted data containing DataFrame records.
    3. Creates or loads the timeseries container and updates the data.
    4. Returns appropriate HTTP status codes.
    """
    tagsubfolder = request.args.get('tagsubfolder')  # Optional
    user = request.args.get('user', 'master')
    columns = request.args.get('columns')
    overwrite = request.args.get('overwrite', 'False') == 'True'
    
    if tagsubfolder is not None:
        tag = tag + '/' + tagsubfolder
    
    try:
        # Handle case where only columns are provided (create empty timeseries)
        if not request.data and columns:
            # Create empty timeseries with specified columns
            columns_list = columns.split(',')
            columns = pd.Index(columns_list)
            
            # Create or update the timeseries using shdata interface
            shdata.timeseries(database, period, source, tag,
                             user=user, columns=columns, overwrite=overwrite)

            response_data = json.dumps({'status': 'success', 'tag': tag, 'message': 'Empty timeseries created with columns'}).encode('utf-8')
            response = Response(response_data, status=201, mimetype='application/json')
            response.headers['Content-Length'] = str(len(response_data))
            return response
        
        # Ensure data is present if no columns specified
        if not request.data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Handle input data (lz4+BSON or JSON)
        content_encoding = request.headers.get('Content-Encoding', '').lower()
        
        if content_encoding == 'lz4':
            # Decompress and decode BSON data
            decompressed = lz4f.decompress(request.data)
            data_payload = bson.decode(decompressed)
            
            if 'data' in data_payload and 'index' in data_payload and 'columns' in data_payload:
                # Binary format with separate index, columns, and data
                index_data = np.frombuffer(data_payload['index'], dtype=np.int64)
                index = pd.to_datetime(index_data)
                columns_list = data_payload['columns']
                shape = data_payload['shape']
                values = np.frombuffer(data_payload['data'], dtype=np.float64).reshape(shape)
                df = pd.DataFrame(values, index=index, columns=columns_list)
            else:
                # Standard BSON with DataFrame-like structure
                df = pd.DataFrame(data_payload)
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
        else:
            # JSON format
            data = json.loads(request.data.decode('utf-8'))
            df = pd.DataFrame(data)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
        
        # Validate that we have a proper DataFrame with datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            return jsonify({'message': 'Data must have a datetime index'}), 400
        
        # Use shdata.timeseries to create or update the timeseries
        # For new timeseries, pass the data via the value parameter
        columns_list = df.columns.tolist() if columns is None else columns.split(',')
        columns = pd.Index(columns_list)
        
        # Create or update the timeseries using shdata interface
        ts = shdata.timeseries(database, period, source, tag,
                         user=user, columns=columns, value=df, overwrite=overwrite)

        icols = df.columns.intersection(ts.columns)
        iindex = df.index.intersection(ts.index)
        ts.loc[iindex, icols] = df.loc[iindex, icols].values

        response_data = json.dumps({'status': 'success', 'tag': tag}).encode('utf-8')
        response = Response(response_data, status=201, mimetype='application/json')
        response.headers['Content-Length'] = str(len(response_data))
        return response
        
    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

def delete_timeseries(database: str, period: str, source: str, tag: str, request):
    """
    Deletes a specified timeseries from the given database, period, and source.
    
    Parameters:
        database (str): The name of the database.
        period (str): The time period associated with the timeseries.
        source (str): The source identifier of the timeseries.
        tag (str): The name of the timeseries tag to delete.
        request (flask.Request): The HTTP request object containing optional query parameters.
    
    Optional Query Parameters in request.args:
        tagsubfolder (str): Optional subfolder appended to the tag name.
        user (str): The user performing the deletion; defaults to 'master' if not provided.
        startdate (str): Start date for partial deletion (delete data from this date onwards).
        enddate (str): End date for partial deletion (delete data up to this date).
    
    Returns:
        flask.Response: HTTP 204 No Content if deletion is successful,
                        HTTP 404 Not Found if the timeseries does not exist.
    """
    tagsubfolder = request.args.get('tagsubfolder')  # Optional
    user = request.args.get('user', 'master')
    startdate = request.args.get('startdate')
    enddate = request.args.get('enddate')
    
    if tagsubfolder is not None:
        tag = tag + '/' + tagsubfolder
    
    try:
        # Use shdata.delete_timeseries for deletion
        if startdate is not None or enddate is not None:
            # For partial deletion, we need to get the data first, modify it, then update
            ts_data = shdata.timeseries(database, period, source, tag, user=user)
            
            if ts_data is None or len(ts_data) == 0:
                return Response(status=404)
            
            # Create a mask for rows to delete
            mask = pd.Series(True, index=ts_data.index)
            
            if startdate is not None:
                startdate = pd.Timestamp(startdate)
                mask = mask & (ts_data.index >= startdate)
                
            if enddate is not None:
                enddate = pd.Timestamp(enddate)
                mask = mask & (ts_data.index <= enddate)
            
            # Set selected rows to NaN (effectively deleting them)
            ts_data.loc[mask, :] = np.nan
            
            # Update the timeseries with modified data
            shdata.timeseries(database, period, source, tag, 
                             user=user, value=ts_data, overwrite=True)
            
            return Response(status=204)
        else:
            # Delete entire timeseries using SharedData delete method
            shdata.delete_timeseries(database, period, source, tag, user=user)
            return Response(status=204)
            
    except Exception as e:
        return Response(status=404)

def write_timeseries(database: str, period: str, source: str, tag: str, request):
    """
    Triggers a write operation for a specified timeseries, persisting data to disk or S3.
    
    This endpoint calls the underlying timeseries container's write() method to flush
    data to persistent storage. This is useful for forcing immediate persistence
    of timeseries data rather than waiting for automatic write operations.
    
    Parameters:
        database (str): The name of the database.
        period (str): The time period associated with the timeseries.
        source (str): The source identifier of the timeseries.
        tag (str): The name of the timeseries tag to write.
        request (flask.Request): The HTTP request object containing optional query parameters.
    
    Optional Query Parameters in request.args:
        tagsubfolder (str): Optional subfolder appended to the tag name.
        user (str): The user performing the write operation; defaults to 'master' if not provided.
        startdate (str): Optional start date for the write operation in ISO format.
    
    Returns:
        flask.Response: HTTP 200 OK if write is successful with operation details,
                        HTTP 404 Not Found if the timeseries does not exist,
                        HTTP 500 Internal Server Error if write operation fails.
    """
    tagsubfolder = request.args.get('tagsubfolder')  # Optional
    user = request.args.get('user', 'master')
    startdate = request.args.get('startdate')
    
    if tagsubfolder is not None:
        tag = tag + '/' + tagsubfolder
    
    try:
        # Construct the path for the timeseries container
        path = f'{user}/{database}/{period}/{source}/timeseries'
        
        # Get the timeseries container from shdata
        if path not in shdata.data:
            return Response(status=404)
        
        ts_container = shdata.data[path]
        
        if ts_container is None:
            return Response(status=404)
        
        # Parse optional startdate parameter
        startdate_obj = None
        if startdate is not None:
            startdate_obj = pd.Timestamp(startdate)
        
        # Call the write method on the container
        ts_container.write(startDate=startdate_obj)
        
        response_data = json.dumps({
            'status': 'success',
            'message': 'Timeseries write operation completed',
            'database': database,
            'period': period,
            'source': source,
            'tag': tag,
            'user': user,
            'startdate': startdate
        }).encode('utf-8')
        
        response = Response(response_data, status=200, mimetype='application/json')
        response.headers['Content-Length'] = str(len(response_data))
        return response
        
    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
