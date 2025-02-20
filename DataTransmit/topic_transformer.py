class TopicTransformer:
    @staticmethod
    def transform_publish_topic(topic):
        topic_mappings = {
            "sensor": "web",
            "TC1": "admin",
            "response": "transmit"
        }
        topic_parts = topic.split("/")
        return "/".join([topic_mappings.get(part, part) for part in topic_parts])
