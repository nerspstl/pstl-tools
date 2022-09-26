from alicat import FlowController as FC


K=FC(port="COM5",address='K')
M=FC(port="COM5",address="M")
N=FC(port="COM5",address="N")

MFCs=[K,M,N]

# set gas type
for k in MFCs:
    k.set_gas('N2')

# set flow rates
for k in MFCs:
    sccm=0

    k.set_flow_rate(sccm)

# view results
for k in MFCs:
    print(k.address)
    print(k.get())
