exports.handler = async (event) => {
    const user = JSON.parse(event.body).user;
    const domain = user.email.split('@')[1]; 

    if(domain === 'aerospike.com' || domain === 'adaptagency.com'){
        return {
            statusCode: 200,
            headers: {
                "content-type": "application/json"
            },
            body: JSON.stringify({"app_metadata": { "roles": ["user"] } })
        }
    }
    
    return {statusCode: 403}     
}