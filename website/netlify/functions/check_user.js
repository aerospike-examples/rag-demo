export const handler = async (_event, context) => {
    const { user } = context.clientContext;
    if(user){
        return {
            statusCode: 200
        }
    }
    else{
        return {
            statusCode: 401,
            body: JSON.stringify('Unauthorized')
        }
    }
}