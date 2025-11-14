from drf_writable_nested import NestedUpdateMixin, WritableNestedModelSerializer


class CustomWritableNestedModelSerializer(WritableNestedModelSerializer):
    """ Necesario porque la clase original no soporta unique_together. """
    def update(self, instance, validated_data):
        relations, reverse_relations = self._extract_relations(validated_data)

        # Create or update direct relations (foreign key, one-to-one)
        self.update_or_create_direct_relations(
            validated_data,
            relations,
        )

        # Update instance
        instance = super(NestedUpdateMixin, self).update(
            instance,
            validated_data,
        )
        self.delete_reverse_relations_if_need(instance, reverse_relations)
        self.update_or_create_reverse_relations(instance, reverse_relations)
        instance.refresh_from_db()
        return instance
