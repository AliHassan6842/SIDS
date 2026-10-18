package com.agrosense.analysis.infrastructure;

import org.springframework.data.redis.connection.stream.ObjectRecord;
import org.springframework.data.redis.stream.StreamListener;
import org.springframework.stereotype.Service;

@Service
public class AIResultConsumer implements StreamListener<String, ObjectRecord<String, String>> {
    @Override
    public void onMessage(ObjectRecord<String, String> message) {
        // Implement AI Result Consumer with manual ack and idempotency
    }
}
