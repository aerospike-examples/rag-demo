from aerospike_vector_search import types, client, admin

vector_seed = types.HostPort(host="aerospike-vector", port=5000)

# Initialize vector admin client
# Used for vector index creation and admin functions 
vector_admin = admin.Client(seeds=vector_seed)

# Initialize vector client 
# Used for writing/reading data to/from Aerospike using the vector index
vector_client = client.Client(seeds=vector_seed)