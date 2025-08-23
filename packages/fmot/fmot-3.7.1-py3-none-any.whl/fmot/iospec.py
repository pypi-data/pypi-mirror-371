from femtorun.user_io_spec import UserIOSpec as _UserIOSpec
from fmot.fqir import GraphProto, TensorProto
from fmot.fqir.writer.fqir_writer import get_bw


class UserIOSpec(_UserIOSpec):
    @classmethod
    def from_fqir(cls, graph: GraphProto, latch_input_names: list[str] = []):
        """Initializes a UserIOSpec object from the given FQIR graph.

        Arguments:
            graph (GraphProto): the FQIR graph
            latch_input_names (list[str]): names of variables that will have latching
                applied. On hardware, latch inputs are not required as inputs for each step -- they will
                instead carry their most recent value until a new value has been sent.
        """
        iospec = cls()
        arith = graph.subgraphs["ARITH"]

        input_names = []
        for x in arith.inputs:
            iospec.add_input(
                varname=x.name,
                length=x.shape[0],
                precision=get_bw(x.dtype),
                quant_scale=2**x.quanta,
                quant_zp=0,
            )
            input_names.append(x.name)

        for name in latch_input_names:
            if name not in input_names:
                raise ValueError(
                    f"latch input {name} was requested, but is not an input to the model"
                )
            input_names.remove(name)

        output_names = []
        for x in arith.outputs:
            iospec.add_output(
                varname=x.name,
                length=x.shape[0],
                precision=get_bw(x.dtype),
                quant_scale=2**x.quanta,
                quant_zp=0,
            )
            output_names.append(x.name)

        iospec.add_signature(
            inputs=input_names, outputs=output_names, latched_inputs=latch_input_names
        )

        for name in input_names:
            iospec.inputs[name]["comments"]["latch"] = False

        for name in latch_input_names:
            iospec.inputs[name]["comments"]["latch"] = True

        iospec.verify()
        return iospec
