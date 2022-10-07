import { EventBus, Rule } from "aws-cdk-lib/aws-events";
import { SqsQueue } from "aws-cdk-lib/aws-events-targets";
import { IFunction } from "aws-cdk-lib/aws-lambda";
import { IQueue } from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";

interface VGTEventBusProps {
    publisherFuntion: IFunction;
    targetQueue: IQueue;
}

export class VGTEventBus extends Construct {

    constructor(scope: Construct, id: string, props: VGTEventBusProps) {
        super(scope, id);

        //eventbus
        const bus = new EventBus(this, 'tr_VGTEventBus', {
            eventBusName: 'tr_VGTEventBus'
        });
    
        const sendOrderRule = new Rule(this, 'tr_SendOrderRule', {
            eventBus: bus,
            enabled: true,
            description: 'When ReviewOrder microservice sends the order',
            eventPattern: {
                source: ['com.vgt.reviewOrder.sendOrder'],
                detailType: ['SendOrder']
            },
            ruleName: 'tr_SendOrderRule'
        });
    
        // // need to pass target to Ordering Lambda service
        // sendOrderRule.addTarget(new LambdaFunction(props.targetFuntion)); 

        // need to pass target to Ordering Lambda service
        sendOrderRule.addTarget(new SqsQueue(props.targetQueue));
        
        bus.grantPutEventsTo(props.publisherFuntion);
            // AccessDeniedException - is not authorized to perform: events:PutEvents

    }

}