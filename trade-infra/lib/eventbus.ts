import { EventBus, Rule } from "aws-cdk-lib/aws-events";
import { SqsQueue } from "aws-cdk-lib/aws-events-targets";
import { IFunction } from "aws-cdk-lib/aws-lambda";
import { IQueue } from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";

interface TEventBusProps {
    publisherFuntion: IFunction;
    targetQueue: IQueue;
}

export class TEventBus extends Construct {

    constructor(scope: Construct, id: string, props: TEventBusProps) {
        super(scope, id);

        //eventbus
        const bus = new EventBus(this, 'tr_EventBus', {
            eventBusName: 'tr_EventBus'
        });
    
        const sendOrderRule = new Rule(this, 'tr_SendOrderRule', {
            eventBus: bus,
            enabled: true,
            description: 'When ReviewOrder microservice sends the trade',
            eventPattern: {
                source: ['com.tr.reviewOrder.sendOrder'],
                detailType: ['tr_SendOrder']
            },
            ruleName: 'tr_SendOrderRule'
        });
    
        // // need to pass target to Ordering Lambda service
        // sendOrderRule.addTarget(new LambdaFunction(props.targetFuntion)); 

        // need to pass target to trade queue 
        sendOrderRule.addTarget(new SqsQueue(props.targetQueue));
        
        // Grant permission for the reviewOrderApi to publish to this event bus
        bus.grantPutEventsTo(props.publisherFuntion);
        // AccessDeniedException - is not authorized to perform: events:PutEvents

    }

}