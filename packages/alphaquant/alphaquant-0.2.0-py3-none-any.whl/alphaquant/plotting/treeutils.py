import alphaquant.cluster.cluster_utils as aqcluster_utils

class TreeSorter():
    def __init__(self, plotconfig, protein):
        self._plotconfig = plotconfig
        self._protein_node = protein
        self._protein_sequence = None
        self._define_protein_sequence_if_applicable()
        

    def get_sorted_tree(self):
        self._sort_tree(self._protein_node)
        return self._protein_node

    def _sort_tree(self, node):
        self._reorder_children(node)
        for child in node.children:
            self._sort_tree(child)

    def _reorder_children(self, parent_node):
        # Get and sort children
        sorted_children = self._get_sorted_children_according_to_plotconfig(parent_node)

        for child in sorted_children:
            child.parent = None  
            child.parent = parent_node

    def _get_sorted_children_according_to_plotconfig(self, protein):
        if self._plotconfig.order_peptides_along_protein_sequence and self._protein_node.type == 'gene' and self._protein_sequence is not None:
            return aqcluster_utils.get_sorted_peptides_by_position_in_protein_seq(protein, self._protein_sequence)
        
        else:
            return aqcluster_utils.get_sorted_peptides_by_cluster(protein)
        
        # else:
        #     return aqcluster_utils.get_sorted_peptides_by_name(protein)
        
    def _define_protein_sequence_if_applicable(self):
        if self._plotconfig.order_peptides_along_protein_sequence:
            self._protein_sequence = self._get_protein_sequence(self._protein_node)



    def _get_protein_sequence(self, protein_node):
        if self._plotconfig.protein_identifier == 'uniprot_id':
            for id in protein_node.name.split(";"):
                try:
                    return self._plotconfig.protid2seq.get(id)
                except:
                    continue
        elif self._plotconfig.protein_identifier == 'gene_symbol':
            try:
                return self._plotconfig.protid2seq.get(protein_node.name)
            except:
                return None
        return None