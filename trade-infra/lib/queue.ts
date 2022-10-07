import { Duration } from "aws-cdk-lib";
import { IFunction } from "aws-cdk-lib/aws-lambda";
import { SqsEventSource } from "aws-cdk-lib/aws-lambda-event-sources";
import { IQueue, Queue } from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";

interface VGTQueueProps {
    consumer: IFunction;
}

export class VGTQueue extends Construct {

    public readonly orderQueue: IQueue;

    constructor(scope: Construct, id: string, props: VGTQueueProps) {
        super(scope, id);

      //queue
      this.orderQueue = new Queue(this, 'tr_OrderQueue', {
        queueName : 'tr_OrderQueue',
        visibilityTimeout: Duration.seconds(30) // default value
      });
      
      props.consumer.addEventSource(new SqsEventSource(this.orderQueue, {
          batchSize: 1
      }));
    }
}