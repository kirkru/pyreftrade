import { Duration } from "aws-cdk-lib";
import { IFunction } from "aws-cdk-lib/aws-lambda";
import { SqsEventSource } from "aws-cdk-lib/aws-lambda-event-sources";
import { IQueue, Queue } from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";

interface TQueueProps {
    consumer: IFunction;
}

export class TQueue extends Construct {

    public readonly tradeQueue: IQueue;

    constructor(scope: Construct, id: string, props: TQueueProps) {
        super(scope, id);

      //queue
      this.tradeQueue = new Queue(this, 'tr_TradeQueue', {
        queueName : 'tr_TradeQueue',
        visibilityTimeout: Duration.seconds(5) // default value = 5 secs
      });
      
      props.consumer.addEventSource(new SqsEventSource(this.tradeQueue, {
          batchSize: 1
      }));
    }
}