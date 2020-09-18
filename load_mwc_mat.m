function out = load_mat( matfile )

m = load(matfile);

% Python Matfiles come in with many additional layers of cell arrays
% This compacts them out
%
out.mwc = [m.MWC{:}]

for p = 1:numel(out.mwc)
  out.mwc(p).beams = [out.mwc(p).beams{:}]
end
